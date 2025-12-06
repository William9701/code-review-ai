"""
Python code analyzer
"""

import ast
from typing import Any, Dict, List

from radon.complexity import cc_visit
from radon.metrics import mi_visit


class PythonAnalyzer:
    """
    Static analyzer for Python code
    """

    def analyze(self, file_path: str, content: str) -> List[Dict[str, Any]]:
        """
        Analyze Python code

        Args:
            file_path: Path to the file
            content: File content

        Returns:
            List of issues found
        """
        issues = []

        try:
            # Parse AST
            tree = ast.parse(content)

            # Check complexity
            issues.extend(self._check_complexity(file_path, content))

            # Check code smells
            issues.extend(self._check_code_smells(file_path, tree))

            # Check maintainability
            issues.extend(self._check_maintainability(file_path, content))

        except SyntaxError as e:
            issues.append(
                {
                    "file_path": file_path,
                    "line_start": e.lineno or 1,
                    "severity": "high",
                    "category": "code_quality",
                    "rule_id": "python_syntax_error",
                    "title": "Syntax Error",
                    "description": f"Syntax error: {e.msg}",
                }
            )

        return issues

    def _check_complexity(self, file_path: str, content: str) -> List[Dict[str, Any]]:
        """Check cyclomatic complexity"""
        issues = []

        try:
            complexity_results = cc_visit(content)

            for result in complexity_results:
                if result.complexity > 15:
                    issues.append(
                        {
                            "file_path": file_path,
                            "line_start": result.lineno,
                            "severity": "medium" if result.complexity <= 20 else "high",
                            "category": "maintainability",
                            "rule_id": "python_high_complexity",
                            "title": f"High Cyclomatic Complexity ({result.complexity})",
                            "description": f"Function '{result.name}' has cyclomatic complexity of {result.complexity}. Consider refactoring to improve maintainability.",
                            "suggested_fix": "Break this function into smaller, more focused functions.",
                            "references": [
                                {
                                    "url": "https://en.wikipedia.org/wiki/Cyclomatic_complexity"
                                }
                            ],
                        }
                    )

        except Exception:
            pass

        return issues

    def _check_code_smells(self, file_path: str, tree: ast.AST) -> List[Dict[str, Any]]:
        """Check for code smells"""
        issues = []

        for node in ast.walk(tree):
            # Check for long functions
            if isinstance(node, ast.FunctionDef):
                func_lines = (
                    node.end_lineno - node.lineno if hasattr(node, "end_lineno") else 0
                )

                if func_lines > 50:
                    issues.append(
                        {
                            "file_path": file_path,
                            "line_start": node.lineno,
                            "severity": "medium",
                            "category": "maintainability",
                            "rule_id": "python_long_function",
                            "title": f"Long Function ({func_lines} lines)",
                            "description": f"Function '{node.name}' is {func_lines} lines long. Consider breaking it into smaller functions.",
                            "suggested_fix": "Extract logical blocks into separate functions.",
                        }
                    )

                # Check for too many parameters
                if len(node.args.args) > 5:
                    issues.append(
                        {
                            "file_path": file_path,
                            "line_start": node.lineno,
                            "severity": "low",
                            "category": "code_quality",
                            "rule_id": "python_too_many_parameters",
                            "title": f"Too Many Parameters ({len(node.args.args)})",
                            "description": f"Function '{node.name}' has {len(node.args.args)} parameters. Consider using a configuration object.",
                            "suggested_fix": "Group related parameters into a dataclass or dictionary.",
                        }
                    )

            # Check for bare except clauses
            if isinstance(node, ast.ExceptHandler):
                if node.type is None:
                    issues.append(
                        {
                            "file_path": file_path,
                            "line_start": node.lineno,
                            "severity": "medium",
                            "category": "best_practices",
                            "rule_id": "python_bare_except",
                            "title": "Bare Except Clause",
                            "description": "Using bare 'except:' can catch unexpected exceptions. Specify the exception type.",
                            "suggested_fix": "Replace 'except:' with 'except Exception:' or specific exception types.",
                        }
                    )

        return issues

    def _check_maintainability(
        self, file_path: str, content: str
    ) -> List[Dict[str, Any]]:
        """Check maintainability index"""
        issues = []

        try:
            mi_results = mi_visit(content, multi=True)

            for mi in mi_results:
                if mi < 20:
                    issues.append(
                        {
                            "file_path": file_path,
                            "line_start": 1,
                            "severity": "medium",
                            "category": "maintainability",
                            "rule_id": "python_low_maintainability",
                            "title": f"Low Maintainability Index ({mi:.1f})",
                            "description": f"File has a low maintainability index of {mi:.1f}. Consider refactoring to improve code quality.",
                            "suggested_fix": "Reduce complexity, improve documentation, and break up large functions.",
                        }
                    )

        except Exception:
            pass

        return issues
