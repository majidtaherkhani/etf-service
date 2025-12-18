#!/usr/bin/env python
"""Script to run tests locally (outside Docker)"""
import sys
import subprocess

def main():
    """Run pytest with proper configuration"""
    cmd = [
        sys.executable, "-m", "pytest",
        "src/modules/etf/tests",
        "-v",
        "--tb=short"
    ]
    
    # Add coverage if pytest-cov is installed
    try:
        import pytest_cov
        cmd.extend(["--cov=src/modules/etf", "--cov-report=term-missing"])
    except ImportError:
        pass
    
    result = subprocess.run(cmd)
    sys.exit(result.returncode)

if __name__ == "__main__":
    main()
