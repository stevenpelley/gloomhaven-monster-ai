import subprocess
import sys
import typing


def main() -> None:
    is_success: bool = True
    for linter_input in [
            ['flake8', '--max-complexity', '8' '.'],
            ['mypy', '--strict', '.'],
            ['pydocstyle', '.'],
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
    """returns true if the linter passes, and false if it fails"""
    p = subprocess.run(args, stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE, text=True)
    if p.returncode != 0:
        print("{} failure:".format(args[0]))
        print(p.stdout)
        return False
    else:
        print("{} success".format(args[0]))
        return True


if __name__ == "__main__":
    main()
