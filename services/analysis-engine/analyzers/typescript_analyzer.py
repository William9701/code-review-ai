"""
TypeScript code analyzer
"""

import re
from typing import Any, Dict, List


class TypeScriptAnalyzer:
    """
    Static analyzer for TypeScript code
    """

    def analyze(self, file_path: str, content: str) -> List[Dict[str, Any]]:
        """
        Analyze TypeScript code

        Args:
            file_path: Path to the file
            content: File content

        Returns:
            List of issues found
        """
        issues = []

        # Check for 'any' type usage
        issues.extend(self._check_any_type(file_path, content))

        # Check for console.log
        issues.extend(self._check_console_log(file_path, content))

        # Check for TODO/FIXME comments
        issues.extend(self._check_todo_comments(file_path, content))

        # Check for == instead of ===
        issues.extend(self._check_loose_equality(file_path, content))

        # Check for missing error handling
        issues.extend(self._check_error_handling(file_path, content))

        return issues

    def _check_any_type(self, file_path: str, content: str) -> List[Dict[str, Any]]:
        """Check for 'any' type usage"""
        issues = []
        lines = content.split("\n")

        for i, line in enumerate(lines, 1):
            if re.search(r":\s*any\b", line):
                issues.append(
                    {
                        "file_path": file_path,
                        "line_start": i,
                        "severity": "low",
                        "category": "code_quality",
                        "rule_id": "typescript_any_type",
                        "title": "Use of 'any' Type",
                        "description": "Using 'any' defeats the purpose of TypeScript. Specify a proper type.",
                        "code_snippet": line.strip(),
                        "suggested_fix": "Replace 'any' with a specific type or use 'unknown' if the type is truly unknown.",
                    }
                )

        return issues

    def _check_console_log(self, file_path: str, content: str) -> List[Dict[str, Any]]:
        """Check for console.log statements"""
        issues = []
        lines = content.split("\n")

        for i, line in enumerate(lines, 1):
            if re.search(r"\bconsole\.(log|debug|info|warn|error)\(", line):
                issues.append(
                    {
                        "file_path": file_path,
                        "line_start": i,
                        "severity": "info",
                        "category": "best_practices",
                        "rule_id": "typescript_console_log",
                        "title": "Console Statement Found",
                        "description": "Console statements should be removed before production deployment.",
                        "code_snippet": line.strip(),
                        "suggested_fix": "Use a proper logging library or remove console statements.",
                    }
                )

        return issues

    def _check_todo_comments(
        self, file_path: str, content: str
    ) -> List[Dict[str, Any]]:
        """Check for TODO/FIXME comments"""
        issues = []
        lines = content.split("\n")

        for i, line in enumerate(lines, 1):
            if re.search(r"//\s*(TODO|FIXME|HACK|XXX)", line, re.IGNORECASE):
                issues.append(
                    {
                        "file_path": file_path,
                        "line_start": i,
                        "severity": "info",
                        "category": "maintainability",
                        "rule_id": "typescript_todo_comment",
                        "title": "TODO Comment",
                        "description": "TODO comment found. Consider creating an issue to track this work.",
                        "code_snippet": line.strip(),
                    }
                )

        return issues

    def _check_loose_equality(
        self, file_path: str, content: str
    ) -> List[Dict[str, Any]]:
        """Check for loose equality (==) instead of strict (===)"""
        issues = []
        lines = content.split("\n")

        for i, line in enumerate(lines, 1):
            if re.search(r"[^=!<>]==[^=]", line) or re.search(r"[^!]==[^=]", line):
                issues.append(
                    {
                        "file_path": file_path,
                        "line_start": i,
                        "severity": "medium",
                        "category": "best_practices",
                        "rule_id": "typescript_loose_equality",
                        "title": "Loose Equality Operator",
                        "description": "Use strict equality (===) instead of loose equality (==).",
                        "code_snippet": line.strip(),
                        "suggested_fix": "Replace '==' with '===' for type-safe comparison.",
                    }
                )

        return issues

    def _check_error_handling(
        self, file_path: str, content: str
    ) -> List[Dict[str, Any]]:
        """Check for missing error handling in async functions"""
        issues = []
        lines = content.split("\n")

        for i, line in enumerate(lines, 1):
            # Look for async functions without try-catch
            if re.search(r"async\s+function", line) or re.search(r"async\s*\(", line):
                # Check if there's a try-catch in the next few lines
                next_lines = "\n".join(lines[i : min(i + 10, len(lines))])
                if "try" not in next_lines and "catch" not in next_lines:
                    issues.append(
                        {
                            "file_path": file_path,
                            "line_start": i,
                            "severity": "medium",
                            "category": "best_practices",
                            "rule_id": "typescript_missing_error_handling",
                            "title": "Missing Error Handling",
                            "description": "Async function should have proper error handling with try-catch.",
                            "suggested_fix": "Add try-catch block to handle potential errors.",
                        }
                    )

        return issues
