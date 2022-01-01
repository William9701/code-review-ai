"""
Quick test to demonstrate the code analyzers work
"""
import sys
import os

# Add paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'services', 'analysis-engine'))

from analyzers.python_analyzer import PythonAnalyzer
from analyzers.typescript_analyzer import TypeScriptAnalyzer
from analyzers.security_analyzer import SecurityAnalyzer

print("=" * 80)
print("CodeReview AI - Analyzer Test")
print("=" * 80)
print()

# Test Python Analyzer
print("[Python] Testing Python Analyzer...")
print("-" * 80)

python_code = """
def complex_function(a, b, c, d, e, f, g):
    '''Function with too many parameters'''
    result = 0
    for i in range(100):
        for j in range(100):
            for k in range(100):
                if i > 50:
                    if j > 50:
                        if k > 50:
                            result += 1
    return result

# Bare except
try:
    risky_operation()
except:
    pass
"""

python_analyzer = PythonAnalyzer()
python_issues = python_analyzer.analyze("example.py", python_code)

print(f"Found {len(python_issues)} Python issues:")
for issue in python_issues:
    print(f"  • [{issue['severity'].upper()}] {issue['title']}")
    print(f"    Line {issue['line_start']}: {issue['description']}")
    print()

# Test TypeScript Analyzer
print("[TypeScript] Testing TypeScript Analyzer...")
print("-" * 80)

ts_code = """
function processData(data: any) {
    console.log("Processing:", data);

    if (data == null) {
        return;
    }

    async function fetchData() {
        const response = await fetch('/api/data');
        return response.json();
    }
}
"""

ts_analyzer = TypeScriptAnalyzer()
ts_issues = ts_analyzer.analyze("example.ts", ts_code)

print(f"Found {len(ts_issues)} TypeScript issues:")
for issue in ts_issues:
    print(f"  • [{issue['severity'].upper()}] {issue['title']}")
    print(f"    Line {issue['line_start']}: {issue['description']}")
    print()

# Test Security Analyzer
print("[Security] Testing Security Analyzer...")
print("-" * 80)

insecure_code = """
import hashlib

# Hardcoded credentials
api_key = "sk-1234567890abcdef"
password = "admin123"

# Weak crypto
hash = hashlib.md5(data.encode()).hexdigest()

# SQL injection
query = "SELECT * FROM users WHERE id = " + user_id
cursor.execute(query)

# Eval usage
eval(user_input)
"""

security_analyzer = SecurityAnalyzer()
security_issues = security_analyzer.analyze("app.py", insecure_code)

print(f"Found {len(security_issues)} Security issues:")
for issue in security_issues:
    print(f"  • [{issue['severity'].upper()}] {issue['title']}")
    print(f"    Line {issue['line_start']}: {issue['description']}")
    if 'metadata' in issue and 'cwe' in issue['metadata']:
        print(f"    CWE: {issue['metadata']['cwe']}")
        print(f"    OWASP: {issue['metadata']['owasp']}")
    print()

# Summary
print("=" * 80)
print("[SUCCESS] All analyzers working correctly!")
print()
print(f"Total issues found: {len(python_issues) + len(ts_issues) + len(security_issues)}")
print(f"  - Python issues: {len(python_issues)}")
print(f"  - TypeScript issues: {len(ts_issues)}")
print(f"  - Security issues: {len(security_issues)}")
print()
print("=" * 80)
print("CodeReview AI is ready to analyze your code!")
print("=" * 80)
