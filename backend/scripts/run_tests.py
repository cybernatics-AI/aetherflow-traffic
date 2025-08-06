#!/usr/bin/env python3
"""
Test Runner Script for AetherFlow Backend
"""

import sys
import os
import subprocess
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def run_tests(test_type="all", verbose=False, coverage=False):
    """Run tests with various options"""
    
    backend_dir = Path(__file__).parent.parent
    os.chdir(backend_dir)
    
    print("🧪 Running AetherFlow Backend Tests...")
    print("-" * 50)
    
    # Base pytest command
    cmd = ["python", "-m", "pytest"]
    
    # Add test directory based on type
    if test_type == "unit":
        cmd.append("tests/unit")
        print("📋 Running unit tests only")
    elif test_type == "integration":
        cmd.append("tests/integration")
        print("📋 Running integration tests only")
    elif test_type == "all":
        cmd.append("tests/")
        print("📋 Running all tests")
    else:
        cmd.append(f"tests/{test_type}")
        print(f"📋 Running tests in: {test_type}")
    
    # Add verbose output if requested
    if verbose:
        cmd.extend(["-v", "-s"])
        print("🔍 Verbose output enabled")
    
    # Add coverage if requested
    if coverage:
        cmd.extend([
            "--cov=aetherflow",
            "--cov-report=html",
            "--cov-report=term-missing",
            "--cov-fail-under=80"
        ])
        print("📊 Code coverage analysis enabled")
    
    # Add other useful options
    cmd.extend([
        "--tb=short",  # Shorter traceback format
        "--strict-markers",  # Strict marker checking
        "--disable-warnings"  # Disable warnings for cleaner output
    ])
    
    try:
        print(f"🚀 Executing: {' '.join(cmd)}")
        print("-" * 50)
        
        result = subprocess.run(cmd, check=False)
        
        if result.returncode == 0:
            print("\n✅ All tests passed!")
            if coverage:
                print("📊 Coverage report generated in htmlcov/index.html")
        else:
            print(f"\n❌ Tests failed with exit code: {result.returncode}")
            
        return result.returncode
        
    except FileNotFoundError:
        print("❌ pytest not found. Please install it with: pip install pytest")
        return 1
    except KeyboardInterrupt:
        print("\n🛑 Tests interrupted by user")
        return 1


def run_linting():
    """Run code linting and formatting checks"""
    
    print("🔍 Running code quality checks...")
    print("-" * 50)
    
    backend_dir = Path(__file__).parent.parent
    os.chdir(backend_dir)
    
    # Check if tools are available
    tools = {
        "black": "Code formatting",
        "isort": "Import sorting",
        "flake8": "Code linting",
        "mypy": "Type checking"
    }
    
    results = {}
    
    for tool, description in tools.items():
        print(f"🔧 {description} ({tool})...")
        
        try:
            if tool == "black":
                cmd = ["black", "--check", "--diff", "src/"]
            elif tool == "isort":
                cmd = ["isort", "--check-only", "--diff", "src/"]
            elif tool == "flake8":
                cmd = ["flake8", "src/"]
            elif tool == "mypy":
                cmd = ["mypy", "src/aetherflow/"]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            results[tool] = result.returncode == 0
            
            if result.returncode == 0:
                print(f"  ✅ {tool} passed")
            else:
                print(f"  ❌ {tool} failed")
                if result.stdout:
                    print(f"     Output: {result.stdout[:200]}...")
                if result.stderr:
                    print(f"     Error: {result.stderr[:200]}...")
                    
        except FileNotFoundError:
            print(f"  ⚠️  {tool} not found - skipping")
            results[tool] = None
    
    print("\n📋 Code Quality Summary:")
    for tool, passed in results.items():
        if passed is True:
            print(f"  ✅ {tool}")
        elif passed is False:
            print(f"  ❌ {tool}")
        else:
            print(f"  ⚠️  {tool} (not available)")
    
    return all(result is not False for result in results.values())


def run_security_check():
    """Run security vulnerability checks"""
    
    print("🔒 Running security checks...")
    print("-" * 50)
    
    try:
        # Check for known vulnerabilities in dependencies
        cmd = ["safety", "check"]
        result = subprocess.run(cmd, check=False)
        
        if result.returncode == 0:
            print("✅ No known security vulnerabilities found")
        else:
            print("❌ Security vulnerabilities detected")
            
        return result.returncode == 0
        
    except FileNotFoundError:
        print("⚠️  safety not found. Install with: pip install safety")
        return True  # Don't fail if tool is not available


def main():
    """Main function"""
    
    import argparse
    
    parser = argparse.ArgumentParser(description="Run AetherFlow Backend Tests")
    parser.add_argument(
        "test_type",
        nargs="?",
        default="all",
        choices=["all", "unit", "integration"],
        help="Type of tests to run"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Verbose output"
    )
    parser.add_argument(
        "-c", "--coverage",
        action="store_true",
        help="Generate coverage report"
    )
    parser.add_argument(
        "-l", "--lint",
        action="store_true",
        help="Run linting and code quality checks"
    )
    parser.add_argument(
        "-s", "--security",
        action="store_true",
        help="Run security vulnerability checks"
    )
    parser.add_argument(
        "--all-checks",
        action="store_true",
        help="Run tests, linting, and security checks"
    )
    
    args = parser.parse_args()
    
    # Check if we're in the right directory
    backend_dir = Path(__file__).parent.parent
    if not (backend_dir / "src" / "aetherflow").exists():
        print("❌ Error: This script must be run from the backend directory")
        sys.exit(1)
    
    success = True
    
    # Run tests
    if not args.lint and not args.security:
        test_result = run_tests(args.test_type, args.verbose, args.coverage)
        success = success and (test_result == 0)
    
    # Run linting if requested
    if args.lint or args.all_checks:
        lint_result = run_linting()
        success = success and lint_result
    
    # Run security checks if requested
    if args.security or args.all_checks:
        security_result = run_security_check()
        success = success and security_result
    
    # Final summary
    print("\n" + "=" * 50)
    if success:
        print("🎉 All checks passed!")
        sys.exit(0)
    else:
        print("❌ Some checks failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
