"""
Analysis Engine Service - Performs static code analysis
"""
import os
import sys
import json
from typing import Dict, Any, List
from datetime import datetime

# Add shared modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from shared.database import (
    get_db_context, Analysis, Issue, PullRequest,
    AnalysisStatus, IssueSeverity, IssueCategory
)
from shared.messaging import get_message_queue
from shared.logging import setup_logging, get_logger

from analyzers.python_analyzer import PythonAnalyzer
from analyzers.typescript_analyzer import TypeScriptAnalyzer
from analyzers.security_analyzer import SecurityAnalyzer

# Setup logging
setup_logging(service_name="analysis-engine")
logger = get_logger(__name__)


class AnalysisEngine:
    """
    Main analysis engine that orchestrates code analysis
    """

    def __init__(self):
        self.analyzers = {
            "python": PythonAnalyzer(),
            "typescript": TypeScriptAnalyzer(),
            "security": SecurityAnalyzer()
        }

    def analyze_pull_request(self, message: Dict[str, Any]) -> None:
        """
        Analyze a pull request

        Args:
            message: Message containing PR information
        """
        pull_request_id = message.get("pull_request_id")
        pr_number = message.get("pr_number")
        head_sha = message.get("head_sha")

        logger.info(
            f"Starting analysis for PR #{pr_number}",
            extra={
                "pull_request_id": pull_request_id,
                "pr_number": pr_number,
                "head_sha": head_sha
            }
        )

        try:
            with get_db_context() as db:
                # Get pull request
                pull_request = db.query(PullRequest).filter(
                    PullRequest.id == pull_request_id
                ).first()

                if not pull_request:
                    logger.error(f"Pull request not found: {pull_request_id}")
                    return

                # Create analysis record
                analysis = Analysis(
                    pull_request_id=pull_request_id,
                    status=AnalysisStatus.IN_PROGRESS,
                    started_at=datetime.utcnow()
                )
                db.add(analysis)
                db.commit()

                analysis_id = analysis.id

            # Fetch PR files and perform analysis
            issues = self._perform_analysis(message)

            # Save results to database
            with get_db_context() as db:
                analysis = db.query(Analysis).filter(
                    Analysis.id == analysis_id
                ).first()

                # Save issues
                for issue_data in issues:
                    issue = Issue(
                        analysis_id=analysis_id,
                        file_path=issue_data["file_path"],
                        line_start=issue_data["line_start"],
                        line_end=issue_data.get("line_end"),
                        column_start=issue_data.get("column_start"),
                        column_end=issue_data.get("column_end"),
                        severity=IssueSeverity(issue_data["severity"]),
                        category=IssueCategory(issue_data["category"]),
                        rule_id=issue_data["rule_id"],
                        title=issue_data["title"],
                        description=issue_data["description"],
                        code_snippet=issue_data.get("code_snippet"),
                        suggested_fix=issue_data.get("suggested_fix"),
                        references=issue_data.get("references"),
                        metadata=issue_data.get("metadata")
                    )
                    db.add(issue)

                # Update analysis statistics
                analysis.status = AnalysisStatus.COMPLETED
                analysis.completed_at = datetime.utcnow()
                analysis.total_issues = len(issues)
                analysis.critical_issues = sum(
                    1 for i in issues if i["severity"] == "critical"
                )
                analysis.high_issues = sum(
                    1 for i in issues if i["severity"] == "high"
                )
                analysis.medium_issues = sum(
                    1 for i in issues if i["severity"] == "medium"
                )
                analysis.low_issues = sum(
                    1 for i in issues if i["severity"] == "low"
                )
                analysis.info_issues = sum(
                    1 for i in issues if i["severity"] == "info"
                )

                if analysis.started_at and analysis.completed_at:
                    duration = (analysis.completed_at - analysis.started_at).total_seconds()
                    analysis.analysis_duration_seconds = duration

                db.commit()

            # Publish results for LLM processing
            queue = get_message_queue()
            queue.publish(
                "analysis.events",
                "analysis.completed",
                {
                    "analysis_id": analysis_id,
                    "pull_request_id": pull_request_id,
                    "total_issues": len(issues),
                    "requires_llm_review": len(issues) > 0
                }
            )

            logger.info(
                f"Analysis completed for PR #{pr_number}",
                extra={
                    "analysis_id": analysis_id,
                    "total_issues": len(issues),
                    "duration_seconds": analysis.analysis_duration_seconds
                }
            )

        except Exception as e:
            logger.error(f"Analysis failed: {e}", exc_info=True)
            # Mark analysis as failed
            with get_db_context() as db:
                if 'analysis_id' in locals():
                    analysis = db.query(Analysis).filter(
                        Analysis.id == analysis_id
                    ).first()
                    if analysis:
                        analysis.status = AnalysisStatus.FAILED
                        analysis.error_message = str(e)
                        analysis.completed_at = datetime.utcnow()
                        db.commit()

    def _perform_analysis(self, message: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Perform static analysis on code files

        Args:
            message: Message containing PR information

        Returns:
            List of issues found
        """
        # TODO: Fetch actual files from GitHub
        # For now, return mock issues

        all_issues = []

        # Mock file analysis
        mock_files = [
            {"path": "src/main.py", "content": "# Python code", "language": "python"},
            {"path": "src/utils.ts", "content": "// TypeScript code", "language": "typescript"}
        ]

        for file_data in mock_files:
            language = file_data["language"]

            if language in self.analyzers:
                analyzer = self.analyzers[language]
                issues = analyzer.analyze(
                    file_data["path"],
                    file_data["content"]
                )
                all_issues.extend(issues)

        # Run security analyzer on all files
        security_analyzer = self.analyzers["security"]
        for file_data in mock_files:
            issues = security_analyzer.analyze(
                file_data["path"],
                file_data["content"]
            )
            all_issues.extend(issues)

        return all_issues


def main():
    """Main worker function"""
    logger.info("Starting Analysis Engine worker")

    engine = AnalysisEngine()
    queue = get_message_queue()

    # Consume messages from analysis queue
    def process_message(message: Dict[str, Any]):
        """Process analysis message"""
        try:
            engine.analyze_pull_request(message)
        except Exception as e:
            logger.error(f"Error processing message: {e}", exc_info=True)

    # Start consuming
    queue.consume("webhook.pr.opened", process_message)
    queue.consume("webhook.pr.synchronized", process_message)


if __name__ == "__main__":
    main()
