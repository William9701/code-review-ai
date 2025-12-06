"""
LLM Service - AI-powered code analysis and suggestions
"""

import json
import os
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional

# Add shared modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from llm_providers.anthropic_provider import AnthropicProvider
from llm_providers.openai_provider import OpenAIProvider

from shared.database import Analysis, Issue, get_db_context
from shared.logging import get_logger, setup_logging
from shared.messaging import get_message_queue

# Setup logging
setup_logging(service_name="llm-service")
logger = get_logger(__name__)


class LLMService:
    """
    Service for AI-powered code review enhancements
    """

    def __init__(self):
        provider = os.getenv("LLM_PROVIDER", "anthropic").lower()

        if provider == "anthropic":
            self.provider = AnthropicProvider()
        elif provider == "openai":
            self.provider = OpenAIProvider()
        else:
            raise ValueError(f"Unknown LLM provider: {provider}")

        logger.info(f"Initialized LLM service with {provider} provider")

    def process_analysis_results(self, message: Dict[str, Any]) -> None:
        """
        Process analysis results and enhance with AI insights

        Args:
            message: Message containing analysis information
        """
        analysis_id = message.get("analysis_id")
        total_issues = message.get("total_issues", 0)

        logger.info(
            f"Processing analysis results with LLM",
            extra={"analysis_id": analysis_id, "total_issues": total_issues},
        )

        if total_issues == 0:
            logger.info("No issues found, skipping LLM processing")
            return

        try:
            with get_db_context() as db:
                # Get analysis and issues
                analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()

                if not analysis:
                    logger.error(f"Analysis not found: {analysis_id}")
                    return

                issues = db.query(Issue).filter(Issue.analysis_id == analysis_id).all()

                # Process issues with LLM
                for issue in issues:
                    # Skip if already has explanation
                    if issue.explanation:
                        continue

                    # Generate explanation and suggestion
                    enhancement = self._enhance_issue(issue)

                    if enhancement:
                        issue.explanation = enhancement.get("explanation")
                        issue.suggested_fix = (
                            enhancement.get("suggested_fix") or issue.suggested_fix
                        )

                db.commit()

            # Publish to GitHub service for posting comments
            queue = get_message_queue()
            queue.publish(
                "github.events",
                "github.comment.create",
                {
                    "analysis_id": analysis_id,
                    "pull_request_id": analysis.pull_request_id,
                },
            )

            logger.info(f"LLM processing completed", extra={"analysis_id": analysis_id})

        except Exception as e:
            logger.error(f"LLM processing failed: {e}", exc_info=True)

    def _enhance_issue(self, issue: Issue) -> Optional[Dict[str, str]]:
        """
        Enhance issue with LLM-generated explanation and fix

        Args:
            issue: Issue object

        Returns:
            Dictionary with explanation and suggested_fix
        """
        try:
            # Build prompt for LLM
            prompt = self._build_prompt(issue)

            # Get LLM response
            response = self.provider.generate(prompt)

            # Parse response
            return self._parse_response(response)

        except Exception as e:
            logger.error(f"Failed to enhance issue: {e}", exc_info=True)
            return None

    def _build_prompt(self, issue: Issue) -> str:
        """
        Build prompt for LLM

        Args:
            issue: Issue object

        Returns:
            Prompt string
        """
        prompt = f"""You are a senior software engineer conducting a code review.

Analyze this code issue and provide:
1. A clear, educational explanation of why this is a problem
2. A specific code suggestion to fix it

Issue Details:
- File: {issue.file_path}
- Line: {issue.line_start}
- Severity: {issue.severity.value}
- Category: {issue.category.value}
- Rule: {issue.rule_id}
- Title: {issue.title}
- Description: {issue.description}

Code snippet:
```
{issue.code_snippet or 'N/A'}
```

Respond in JSON format:
{{
  "explanation": "Detailed explanation of the issue and its impact...",
  "suggested_fix": "Concrete code example showing how to fix it..."
}}

Be concise, educational, and actionable. Focus on WHY this matters and HOW to fix it."""

        return prompt

    def _parse_response(self, response: str) -> Dict[str, str]:
        """
        Parse LLM response

        Args:
            response: Raw LLM response

        Returns:
            Parsed response dictionary
        """
        try:
            # Try to extract JSON from response
            if "```json" in response:
                json_start = response.find("```json") + 7
                json_end = response.find("```", json_start)
                response = response[json_start:json_end].strip()
            elif "```" in response:
                json_start = response.find("```") + 3
                json_end = response.find("```", json_start)
                response = response[json_start:json_end].strip()

            return json.loads(response)

        except json.JSONDecodeError:
            # Fallback: use entire response as explanation
            return {"explanation": response, "suggested_fix": None}


def main():
    """Main worker function"""
    logger.info("Starting LLM Service worker")

    service = LLMService()
    queue = get_message_queue()

    # Consume messages from analysis results queue
    def process_message(message: Dict[str, Any]):
        """Process analysis results message"""
        try:
            if message.get("requires_llm_review", False):
                service.process_analysis_results(message)
        except Exception as e:
            logger.error(f"Error processing message: {e}", exc_info=True)

    # Start consuming
    queue.consume("analysis.results", process_message)


if __name__ == "__main__":
    main()
