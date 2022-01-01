"""
GitHub Service - Handles GitHub API interactions
"""
import os
import sys
import json
import time
from typing import Dict, Any, List
from datetime import datetime
import jwt
from github import Github, GithubIntegration, Auth

# Add shared modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from shared.database import get_db_context, Analysis, Issue, PullRequest, Repository
from shared.messaging import get_message_queue
from shared.logging import setup_logging, get_logger

# Setup logging
setup_logging(service_name="github-service")
logger = get_logger(__name__)


class GitHubService:
    """
    Service for GitHub API interactions
    """

    def __init__(self):
        self.app_id = os.getenv("GITHUB_APP_ID")
        private_key = os.getenv("GITHUB_PRIVATE_KEY", "").replace("\\n", "\n")

        if not self.app_id or not private_key:
            raise ValueError("GITHUB_APP_ID and GITHUB_PRIVATE_KEY must be set")

        self.private_key = private_key
        self.integration = GithubIntegration(
            auth=Auth.AppAuth(
                self.app_id,
                self.private_key
            )
        )

    def get_installation_client(self, installation_id: int) -> Github:
        """
        Get GitHub client for specific installation

        Args:
            installation_id: GitHub App installation ID

        Returns:
            Authenticated GitHub client
        """
        auth = self.integration.get_access_token(installation_id)
        return Github(auth=Auth.Token(auth.token))

    def post_review_comments(self, message: Dict[str, Any]) -> None:
        """
        Post review comments on PR

        Args:
            message: Message containing analysis information
        """
        analysis_id = message.get("analysis_id")
        pull_request_id = message.get("pull_request_id")

        logger.info(
            f"Posting review comments",
            extra={
                "analysis_id": analysis_id,
                "pull_request_id": pull_request_id
            }
        )

        try:
            with get_db_context() as db:
                # Get analysis, PR, and repository
                analysis = db.query(Analysis).filter(
                    Analysis.id == analysis_id
                ).first()

                if not analysis:
                    logger.error(f"Analysis not found: {analysis_id}")
                    return

                pull_request = db.query(PullRequest).filter(
                    PullRequest.id == pull_request_id
                ).first()

                if not pull_request:
                    logger.error(f"Pull request not found: {pull_request_id}")
                    return

                repository = db.query(Repository).filter(
                    Repository.id == pull_request.repository_id
                ).first()

                if not repository:
                    logger.error(f"Repository not found: {pull_request.repository_id}")
                    return

                # Get issues to comment on
                issues = db.query(Issue).filter(
                    Issue.analysis_id == analysis_id
                ).all()

                # Get GitHub client
                gh = self.get_installation_client(repository.installation_id)
                repo = gh.get_repo(repository.full_name)
                pr = repo.get_pull(pull_request.pr_number)

                # Post comments
                comments_posted = 0
                for issue in issues:
                    # Skip if already commented
                    if issue.github_comment_id:
                        continue

                    # Build comment body
                    comment_body = self._format_comment(issue)

                    try:
                        # Post review comment on specific line
                        comment = pr.create_review_comment(
                            body=comment_body,
                            commit=pr.head,
                            path=issue.file_path,
                            line=issue.line_start
                        )

                        # Save comment ID
                        issue.github_comment_id = comment.id
                        comments_posted += 1

                        logger.debug(
                            f"Posted comment on {issue.file_path}:{issue.line_start}"
                        )

                        # Rate limiting - be nice to GitHub
                        time.sleep(0.5)

                    except Exception as e:
                        logger.error(f"Failed to post comment: {e}")

                db.commit()

                # Post summary comment
                self._post_summary_comment(pr, analysis, issues)

                logger.info(
                    f"Posted {comments_posted} review comments",
                    extra={
                        "analysis_id": analysis_id,
                        "comments_posted": comments_posted
                    }
                )

        except Exception as e:
            logger.error(f"Failed to post review comments: {e}", exc_info=True)

    def _format_comment(self, issue: Issue) -> str:
        """
        Format issue as GitHub comment

        Args:
            issue: Issue object

        Returns:
            Formatted comment markdown
        """
        severity_emoji = {
            "critical": "🚨",
            "high": "⚠️",
            "medium": "⚡",
            "low": "💡",
            "info": "ℹ️"
        }

        category_emoji = {
            "security": "🔒",
            "performance": "⚡",
            "code_quality": "✨",
            "best_practices": "👍",
            "maintainability": "🔧"
        }

        emoji = severity_emoji.get(issue.severity.value, "")
        cat_emoji = category_emoji.get(issue.category.value, "")

        comment = f"## {emoji} {issue.title}\n\n"
        comment += f"**Category:** {cat_emoji} {issue.category.value.replace('_', ' ').title()}  \n"
        comment += f"**Severity:** {issue.severity.value.upper()}  \n"
        comment += f"**Rule:** `{issue.rule_id}`\n\n"

        comment += f"### Description\n{issue.description}\n\n"

        if issue.explanation:
            comment += f"### Why This Matters\n{issue.explanation}\n\n"

        if issue.suggested_fix:
            comment += f"### Suggested Fix\n```\n{issue.suggested_fix}\n```\n\n"

        if issue.references:
            comment += "### References\n"
            for ref in issue.references:
                comment += f"- [{ref.get('title', ref.get('url'))}]({ref.get('url')})\n"
            comment += "\n"

        comment += "---\n"
        comment += "*🤖 This comment was generated by [CodeReview AI](https://github.com/yourusername/code-review-ai)*"

        return comment

    def _post_summary_comment(
        self,
        pr,
        analysis: Analysis,
        issues: List[Issue]
    ) -> None:
        """
        Post summary comment on PR

        Args:
            pr: GitHub PR object
            analysis: Analysis object
            issues: List of issues
        """
        try:
            summary = "## 🤖 Code Review Summary\n\n"
            summary += f"**Analysis completed** in {analysis.analysis_duration_seconds:.1f}s\n\n"

            if analysis.total_issues == 0:
                summary += "✅ **No issues found!** Great work! 🎉\n"
            else:
                summary += f"Found **{analysis.total_issues} issue(s)**:\n\n"
                summary += f"- 🚨 Critical: {analysis.critical_issues}\n"
                summary += f"- ⚠️ High: {analysis.high_issues}\n"
                summary += f"- ⚡ Medium: {analysis.medium_issues}\n"
                summary += f"- 💡 Low: {analysis.low_issues}\n"
                summary += f"- ℹ️ Info: {analysis.info_issues}\n\n"

                # Group by category
                categories = {}
                for issue in issues:
                    cat = issue.category.value
                    categories[cat] = categories.get(cat, 0) + 1

                summary += "### Issues by Category\n"
                for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
                    summary += f"- {cat.replace('_', ' ').title()}: {count}\n"

                summary += "\n"

            summary += "---\n"
            summary += "*🤖 Generated by [CodeReview AI](https://github.com/yourusername/code-review-ai)*"

            # Post as issue comment (not review comment)
            pr.create_issue_comment(summary)

            logger.info("Posted summary comment")

        except Exception as e:
            logger.error(f"Failed to post summary comment: {e}")


def main():
    """Main worker function"""
    logger.info("Starting GitHub Service worker")

    service = GitHubService()
    queue = get_message_queue()

    # Consume messages from GitHub events queue
    def process_message(message: Dict[str, Any]):
        """Process GitHub event message"""
        try:
            service.post_review_comments(message)
        except Exception as e:
            logger.error(f"Error processing message: {e}", exc_info=True)

    # Start consuming
    queue.consume("github.comments", process_message)


if __name__ == "__main__":
    main()
