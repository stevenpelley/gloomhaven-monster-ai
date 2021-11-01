"""Run tests for project."""

import subprocess
import sys


def main() -> None:
    """Run the main code for tests."""
    p = subprocess.run(['pytest',
                        '--cov=src',
                        '--cov-fail-under=100',
                        '--no-cov-on-fail',
                        '--cov-report=term-missing',
                        '.'],
                       stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE,
                       text=True)
    print(p.stdout)
    if p.returncode != 0:
        print("tests failed")
        sys.exit(-1)
    else:
        print("tests succeeded")
        sys.exit(0)


if __name__ == "__main__":
    """Run the main function if running as a script."""
    main()
