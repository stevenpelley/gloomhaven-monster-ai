import json
import pytest
import typing


class A(object):
    def json_default(self) -> typing.Any:
        """Define serialization."""
        return [1, 2, 3]


class B(object):
    def __init__(self, obj: typing.Any):
        self.obj = obj

    def json_default(self) -> typing.Any:
        """Define serialization."""
        return {"obj": self.obj}


class C(object):
    pass


def test_json_monkey_patch() -> None:
    """test that json serialization works.

    Classes/objects with json_default() should use that method
    to provide a serializable object.
    Objects without should use normal serialization."""
    assert json.dumps({"a": 1}) == '{"a": 1}'

    obj = {
        "a": A(),
        "b with a": B(A()),
        "b with b with dict": B(B({"asdf": 1}))}
    s = json.dumps(obj)
    assert s == ('{"a": [1, 2, 3], "b with a": {"obj": [1, 2, 3]},'
                 ' "b with b with dict": {"obj": {"obj": {"asdf": 1}}}}')

    with pytest.raises(
            TypeError,
            match="Object of type C is not JSON serializable"):
        json.dumps(C())

    with pytest.raises(
            TypeError,
            match="Object of type C is not JSON serializable"):
        json.dumps({"a": C()})

    with pytest.raises(
            TypeError,
            match="Object of type C is not JSON serializable"):
        json.dumps(B(C()))
