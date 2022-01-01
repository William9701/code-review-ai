"""
Security vulnerability analyzer
"""
import re
from typing import List, Dict, Any


class SecurityAnalyzer:
    """
    Security-focused static analyzer
    """

    def __init__(self):
        # Security patterns to detect
        self.patterns = {
            "sql_injection": {
                "patterns": [
                    r'execute\s*\(\s*["\'].*?\%s',
                    r'cursor\.execute\s*\(\s*f["\']',
                    r'query\s*=\s*["\'].*?\+.*?["\']',
                    r'=\s*["\']SELECT.*?["\'].*?\+',  # String concat after query
                    r'\+.*?["\'].*?SELECT',  # String concat before query
                ],
                "severity": "critical",
                "title": "Potential SQL Injection",
                "description": "SQL query constructed using string concatenation or formatting. Use parameterized queries instead.",
                "cwe": "CWE-89"
            },
            "hardcoded_secret": {
                "patterns": [
                    r'password\s*=\s*["\'][^"\']+["\']',
                    r'api[_-]?key\s*=\s*["\'][^"\']+["\']',
                    r'secret\s*=\s*["\'][^"\']+["\']',
                    r'token\s*=\s*["\'][a-zA-Z0-9]{20,}["\']',
                ],
                "severity": "critical",
                "title": "Hardcoded Secret",
                "description": "Hardcoded credential detected. Use environment variables or a secrets manager.",
                "cwe": "CWE-798"
            },
            "path_traversal": {
                "patterns": [
                    r'open\s*\(\s*[^)]*\+',
                    r'readFile\s*\(\s*[^)]*\+',
                    r'\.\./',
                ],
                "severity": "high",
                "title": "Potential Path Traversal",
                "description": "File path constructed from user input without validation.",
                "cwe": "CWE-22"
            },
            "weak_crypto": {
                "patterns": [
                    r'hashlib\.md5',
                    r'hashlib\.sha1',
                    r'DES|RC4|MD5|SHA1',
                ],
                "severity": "high",
                "title": "Weak Cryptographic Algorithm",
                "description": "Using weak cryptographic algorithm. Use SHA-256 or stronger.",
                "cwe": "CWE-327"
            },
            "xss": {
                "patterns": [
                    r'dangerouslySetInnerHTML',
                    r'innerHTML\s*=',
                    r'document\.write\s*\(',
                ],
                "severity": "high",
                "title": "Potential XSS Vulnerability",
                "description": "Direct HTML manipulation can lead to XSS attacks. Sanitize user input.",
                "cwe": "CWE-79"
            },
            "eval_usage": {
                "patterns": [
                    r'\beval\s*\(',
                    r'exec\s*\(',
                    r'Function\s*\(',
                ],
                "severity": "high",
                "title": "Use of eval() or exec()",
                "description": "Using eval() or exec() can lead to code injection. Avoid if possible.",
                "cwe": "CWE-95"
            },
            "insecure_random": {
                "patterns": [
                    r'Math\.random\s*\(',
                    r'random\.random\s*\(',
                ],
                "severity": "medium",
                "title": "Insecure Random Number Generation",
                "description": "Using non-cryptographic random for security purposes. Use crypto.randomBytes() or secrets module.",
                "cwe": "CWE-330"
            },
            "debug_mode": {
                "patterns": [
                    r'DEBUG\s*=\s*True',
                    r'debug:\s*true',
                ],
                "severity": "medium",
                "title": "Debug Mode Enabled",
                "description": "Debug mode should be disabled in production.",
                "cwe": "CWE-489"
            }
        }

    def analyze(self, file_path: str, content: str) -> List[Dict[str, Any]]:
        """
        Analyze code for security vulnerabilities

        Args:
            file_path: Path to the file
            content: File content

        Returns:
            List of security issues found
        """
        issues = []
        lines = content.split('\n')

        for rule_id, rule_config in self.patterns.items():
            for pattern in rule_config["patterns"]:
                for i, line in enumerate(lines, 1):
                    if re.search(pattern, line, re.IGNORECASE):
                        issues.append({
                            "file_path": file_path,
                            "line_start": i,
                            "severity": rule_config["severity"],
                            "category": "security",
                            "rule_id": f"security_{rule_id}",
                            "title": rule_config["title"],
                            "description": rule_config["description"],
                            "code_snippet": line.strip(),
                            "metadata": {
                                "cwe": rule_config.get("cwe"),
                                "owasp": self._get_owasp_category(rule_id)
                            },
                            "references": [
                                {"url": f"https://cwe.mitre.org/data/definitions/{rule_config.get('cwe', '').replace('CWE-', '')}.html"}
                            ] if rule_config.get("cwe") else []
                        })

        return issues

    def _get_owasp_category(self, rule_id: str) -> str:
        """Map rule to OWASP Top 10 category"""
        owasp_mapping = {
            "sql_injection": "A03:2021 - Injection",
            "hardcoded_secret": "A07:2021 - Identification and Authentication Failures",
            "path_traversal": "A01:2021 - Broken Access Control",
            "weak_crypto": "A02:2021 - Cryptographic Failures",
            "xss": "A03:2021 - Injection",
            "eval_usage": "A03:2021 - Injection",
            "insecure_random": "A02:2021 - Cryptographic Failures",
            "debug_mode": "A05:2021 - Security Misconfiguration"
        }
        return owasp_mapping.get(rule_id, "")
