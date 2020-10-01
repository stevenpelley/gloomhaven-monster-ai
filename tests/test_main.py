import main.main


def test_main() -> None:
    assert main.main.test_func_with_type("nothing")
    assert not main.main.test_func_with_type("something")
    # shouldn't throw
    main.main.main()
