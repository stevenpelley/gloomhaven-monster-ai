import src.main


def test_main() -> None:
    assert src.main.test_func_with_type("nothing")
    assert not src.main.test_func_with_type("something")
    # shouldn't throw
    src.main.main()
