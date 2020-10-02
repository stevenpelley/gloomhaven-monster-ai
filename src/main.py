"""Execute main, test logic.  To be replaced."""


def main() -> None:
    """Run the main function and logic."""
    s = "eric writes silly variable names"
    test_string = "Hello"
    print("{} - {}".format(s, test_string))


def test_func_with_type(arg: str) -> bool:
    """Return an arbitrary comparison."""
    return arg == "nothing"


if __name__ == '__main__':
    """Run the main function as a script."""
    main()
