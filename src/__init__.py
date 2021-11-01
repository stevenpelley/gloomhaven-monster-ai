"""Primary package."""
import json
import typing


# monkey patch json's encoder to search for a to_json method
# if found default() returns the result of to_json
_original_default = json.JSONEncoder().default


def _default(self: json.JSONEncoder, o: typing.Any) -> typing.Any:
    try:
        f = getattr(o.__class__, "json_default")
    except AttributeError:
        return _original_default(o)
    else:
        return f(o)


# ignore typing.  mypy doesn't like assigning a function/method,
# but this is the essence of monkey patching
json.JSONEncoder.default = _default  # type: ignore
