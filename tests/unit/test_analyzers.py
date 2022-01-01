"""
Unit tests for code analyzers
"""
import sys
import os

# Add paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'services', 'analysis-engine'))

from analyzers.python_analyzer import PythonAnalyzer
from analyzers.typescript_analyzer import TypeScriptAnalyzer
from analyzers.security_analyzer import SecurityAnalyzer


def test_python_analyzer_complexity():
    """Test Python complexity detection"""
    analyzer = PythonAnalyzer()
    # Create a function with complexity > 15
    code = """
def complex_function(a, b, c, d):
    result = 0
    if a > 0:
        if b > 0:
            if c > 0:
                if d > 0:
                    for i in range(10):
                        if i % 2 == 0:
                            if i > 5:
                                result += 1
                            elif i > 3:
                                result += 2
                            else:
                                result -= 1
                        else:
                            if i < 3:
                                result += 2
                            elif i < 7:
                                result += 3
                            else:
                                result -= 2
                    for j in range(5):
                        if j > 2:
                            result *= 2
                        elif j == 1:
                            result *= 3
                        elif j == 0:
                            result *= 4
                        else:
                            result *= 5
                    if result > 100:
                        result = 0
                else:
                    result = 10
            else:
                result = 1
        else:
            result = 2
    else:
        result = 3
    return result
"""
    issues = analyzer.analyze("test.py", code)
    # Should detect high complexity
    assert any(i['rule_id'] == 'python_high_complexity' for i in issues)
    print("[PASS] Python complexity detection")


def test_python_analyzer_parameters():
    """Test Python too many parameters detection"""
    analyzer = PythonAnalyzer()
    code = """
def func(a, b, c, d, e, f, g):
    pass
"""
    issues = analyzer.analyze("test.py", code)
    # Should detect too many parameters
    assert any(i['rule_id'] == 'python_too_many_parameters' for i in issues)
    print("[PASS] Python parameter count detection")


def test_typescript_analyzer_any_type():
    """Test TypeScript 'any' type detection"""
    analyzer = TypeScriptAnalyzer()
    code = "function test(data: any) { return data; }"
    issues = analyzer.analyze("test.ts", code)
    # Should detect 'any' usage
    assert any(i['rule_id'] == 'typescript_any_type' for i in issues)
    print("[PASS] TypeScript 'any' type detection")


def test_typescript_analyzer_console():
    """Test TypeScript console.log detection"""
    analyzer = TypeScriptAnalyzer()
    code = "console.log('debug');"
    issues = analyzer.analyze("test.ts", code)
    # Should detect console.log
    assert any(i['rule_id'] == 'typescript_console_log' for i in issues)
    print("[PASS] TypeScript console.log detection")


def test_security_analyzer_sql_injection():
    """Test SQL injection detection"""
    analyzer = SecurityAnalyzer()
    code = """
query = "SELECT * FROM users WHERE id = " + user_id
cursor.execute(query)
"""
    issues = analyzer.analyze("test.py", code)
    # Should detect SQL injection
    assert any(i['rule_id'] == 'security_sql_injection' for i in issues)
    assert any(i['severity'] == 'critical' for i in issues)
    print("[PASS] SQL injection detection")


def test_security_analyzer_hardcoded_secret():
    """Test hardcoded secret detection"""
    analyzer = SecurityAnalyzer()
    code = 'api_key = "sk-1234567890abcdef"'
    issues = analyzer.analyze("test.py", code)
    # Should detect hardcoded secret
    assert any(i['rule_id'] == 'security_hardcoded_secret' for i in issues)
    assert any(i['severity'] == 'critical' for i in issues)
    print("[PASS] Hardcoded secret detection")


def test_security_analyzer_weak_crypto():
    """Test weak cryptography detection"""
    analyzer = SecurityAnalyzer()
    code = "hash = hashlib.md5(data).hexdigest()"
    issues = analyzer.analyze("test.py", code)
    # Should detect weak crypto
    assert any(i['rule_id'] == 'security_weak_crypto' for i in issues)
    print("[PASS] Weak cryptography detection")


def test_security_analyzer_xss():
    """Test XSS vulnerability detection"""
    analyzer = SecurityAnalyzer()
    code = "element.innerHTML = userInput;"
    issues = analyzer.analyze("test.js", code)
    # Should detect XSS
    assert any(i['rule_id'] == 'security_xss' for i in issues)
    print("[PASS] XSS vulnerability detection")


def test_security_analyzer_cwe_mapping():
    """Test CWE and OWASP mapping"""
    analyzer = SecurityAnalyzer()
    code = """
password = "admin123"
query = "SELECT * FROM users WHERE id = " + user_id
"""
    issues = analyzer.analyze("test.py", code)

    # Check metadata exists
    for issue in issues:
        assert 'metadata' in issue
        assert 'cwe' in issue['metadata']
        assert 'owasp' in issue['metadata']

    print("[PASS] CWE/OWASP mapping")


def run_all_tests():
    """Run all tests"""
    print("=" * 60)
    print("Running Unit Tests")
    print("=" * 60)
    print()

    tests = [
        test_python_analyzer_complexity,
        test_python_analyzer_parameters,
        test_typescript_analyzer_any_type,
        test_typescript_analyzer_console,
        test_security_analyzer_sql_injection,
        test_security_analyzer_hardcoded_secret,
        test_security_analyzer_weak_crypto,
        test_security_analyzer_xss,
        test_security_analyzer_cwe_mapping,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"[FAIL] {test.__name__}: {e}")
            failed += 1
        except Exception as e:
            print(f"[ERROR] {test.__name__}: {e}")
            failed += 1

    print()
    print("=" * 60)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("=" * 60)

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
