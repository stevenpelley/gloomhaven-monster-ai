import subprocess
import sys
import typing


def main() -> None:
    is_success: bool = True
    p = subprocess.run(['pytest'], stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE, text=True)
    for test_input in [
        ['pytest', '.'],
        ['pytest', '--cov=main', '.'],
    ]:
        this_success = run_tests(test_input)
        is_success = is_success and this_success

    if is_success:
        print("all tests pass")
        sys.exit(0)
    else:
        print("test failure")
        sys.exit(-1)


def run_tests(args: typing.List[str]) -> bool:
    """returns true if the linter passes, and false if it fails"""
    p = subprocess.run(args, stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE, text=True)
    print(p.stdout)
    if p.returncode != 0:
        print("{} failure:".format(args[0]))
        print(p.stdout)
        return False
    else:
        print("{} success".format(args[0]))
        return True


if __name__ == "__main__":
    main()
