def main() -> None:
    s = "eric writes silly variable names"
    test_string = "Hello"
    print("{} - {}".format(s, test_string))


def test_func_with_type(arg: str) -> bool:
    return arg == "nothing"


if __name__ == '__main__':
    main()
