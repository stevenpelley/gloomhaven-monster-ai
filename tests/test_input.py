import json

import jsonschema  # type: ignore
import pytest
import src.inputdto
import typing


def _simple_valid_json_dict() -> dict[str, typing.Any]:
    """create a minimal valid json document as a dict."""
    return {
        "characters": [{
            "name": "rogue",
            "initiative": 9,
            "initiative2": 10,
            "x": 10,
            "y": 10,
        }],
        "monsters": [{
            "name": "living bones",
            "number": 1,
            "initiative": 50,
            "x": 15,
            "y": 15,
        }],
        "mm_name": "living bones",
        "mm_num": 1,
    }


def test_input_failures() -> None:
    # invalid json
    with pytest.raises(json.JSONDecodeError):
        src.inputdto.decode('asdf')

    # not a json object
    with pytest.raises(
            jsonschema.ValidationError,
            match="""'asdf' is not of type 'object"""):
        src.inputdto.decode('''"asdf"''')

    # does not contain correct keys

    d = _simple_valid_json_dict()
    del d["characters"]
    with pytest.raises(
            jsonschema.ValidationError,
            match="""'characters' is a required property"""):
        src.inputdto.decode(json.dumps(d))

    d = _simple_valid_json_dict()
    del d["monsters"]
    with pytest.raises(
            jsonschema.ValidationError,
            match="""'monsters' is a required property"""):
        src.inputdto.decode(json.dumps(d))

    d = _simple_valid_json_dict()
    del d["mm_name"]
    with pytest.raises(
            jsonschema.ValidationError,
            match="'mm_name' is a required property"):
        src.inputdto.decode(json.dumps(d))

    d = _simple_valid_json_dict()
    del d["mm_num"]
    with pytest.raises(
            jsonschema.ValidationError,
            match="'mm_num' is a required property"):
        src.inputdto.decode(json.dumps(d))

    d = _simple_valid_json_dict()
    d["asdf"] = 2
    with pytest.raises(
            jsonschema.ValidationError,
            # parentheses escaped so that it does not infer regex
            match=("""Additional properties are not allowed """
                   """\\('asdf' was unexpected\\)""")):
        src.inputdto.decode(json.dumps(d))

    d = _simple_valid_json_dict()
    d["characters"] = []
    with pytest.raises(
            jsonschema.ValidationError,
            match='\\[\\] is too short') as excinfo:
        src.inputdto.decode(json.dumps(d))
    assert excinfo.value.json_path == "$.characters"

    d = _simple_valid_json_dict()
    d["monsters"] = []
    with pytest.raises(
            jsonschema.ValidationError,
            match='\\[\\] is too short') as excinfo:
        src.inputdto.decode(json.dumps(d))
    assert excinfo.value.json_path == "$.monsters"

    # incorrect types

    d = _simple_valid_json_dict()
    d["characters"] = "asdf"
    with pytest.raises(
            jsonschema.ValidationError,
            match="'asdf' is not of type 'array'") as excinfo:
        src.inputdto.decode(json.dumps(d))
    assert excinfo.value.json_path == "$.characters"

    d = _simple_valid_json_dict()
    d["mm_name"] = 0
    with pytest.raises(
            jsonschema.ValidationError,
            match="0 is not of type 'string'") as excinfo:
        src.inputdto.decode(json.dumps(d))
    assert excinfo.value.json_path == "$.mm_name"

    d = _simple_valid_json_dict()
    d["mm_num"] = "asdf"
    with pytest.raises(
            jsonschema.ValidationError,
            match="'asdf' is not of type 'integer'") as excinfo:
        src.inputdto.decode(json.dumps(d))
    assert excinfo.value.json_path == "$.mm_num"

    d = _simple_valid_json_dict()
    d["monsters"] = "asdf"
    with pytest.raises(
            jsonschema.ValidationError,
            match="'asdf' is not of type 'array'") as excinfo:
        src.inputdto.decode(json.dumps(d))
    assert excinfo.value.json_path == "$.monsters"

    d = _simple_valid_json_dict()
    d["characters"][0]["initiative"] = 100
    with pytest.raises(
            ValueError,
            match=("initiative must be less than or "
                   "equal to initiative2: 100 10")):
        src.inputdto.decode(json.dumps(d))

    # duplicate character
    d = _simple_valid_json_dict()
    d["characters"] = [{
        "name": "rogue",
        "initiative": 9,
        "initiative2": 10,
        "x": 10,
        "y": 10,
    }, {
        "name": "rogue",
        "initiative": 9,
        "initiative2": 10,
        "x": 11,
        "y": 11,
    }, ]
    with pytest.raises(
            ValueError,
            match="duplicate character name: rogue"):
        src.inputdto.decode(json.dumps(d))

    # duplicate monster
    d = _simple_valid_json_dict()
    d["monsters"] = [{
        "name": "living bones",
        "number": 1,
        "initiative": 50,
        "x": 15,
        "y": 15,
    }, {
        "name": "living bones",
        "number": 1,
        "initiative": 50,
        "x": 16,
        "y": 16,
    }, ]
    with pytest.raises(
            ValueError,
            match="duplicate monster label: \\('living bones', 1\\)"):
        src.inputdto.decode(json.dumps(d))

    # character and monster occupy same hex
    d = _simple_valid_json_dict()
    d['characters'][0]['x'] = 1
    d['characters'][0]['y'] = 1
    d['monsters'][0]['x'] = 1
    d['monsters'][0]['y'] = 1
    with pytest.raises(
            ValueError,
            match="two objects occupy the same hex"):
        src.inputdto.decode(json.dumps(d))


def test_str() -> None:
    d = _simple_valid_json_dict()
    my_input = src.inputdto.decode(json.dumps(d))
    s = str(my_input)
    # make sure it is valid json
    json.loads(s)
    s = str(my_input.characters[0])
    json.loads(s)
    s = str(my_input.monsters[0])
    json.loads(s)


def test_inputs() -> None:
    # minimal successful input.
    d = _simple_valid_json_dict()
    my_input = src.inputdto.decode(json.dumps(d))

    assert my_input._dct is not None
    assert len(my_input.characters) == 1
    assert len(my_input.monsters) == 1
    assert my_input.mm_num == 1
    assert my_input.mm_name == "living bones"
