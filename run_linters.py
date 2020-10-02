"""Run script for all linters."""
import subprocess
import sys
import typing


def main() -> None:
    """Run all linters.

    Linter output will be sent to stdout.
    This function will exit the script with return code 0 on success, and other
    value on failure.
    """
    is_success: bool = True
    for linter_input in [
            ['flake8', '--max-complexity', '8', '.'],
            ['mypy', '--strict', '.'],
            ['pydocstyle', '.'],
            ['autopep8', '-r', '-d', '-a', '-a', '--exit-code', '.']
    ]:
        this_success = run_single_linter(linter_input)
        is_success = is_success and this_success

    if is_success:
        print("all linters pass")
        sys.exit(0)
    else:
        print("linter failure")
        sys.exit(-1)


def run_single_linter(args: typing.List[str]) -> bool:
    """Return true if the linter passes, and false if it fails."""
    p = subprocess.run(args, stdout=subprocess.PIPE,
                       stderr=subprocess.STDOUT, text=True)
    if p.returncode != 0:
        print("{} failure:".format(args[0]))
        print(p.stdout)
        return False
    else:
        print("{} success".format(args[0]))
        return True


if __name__ == "__main__":
    """Run the main function as a script."""
    main()
