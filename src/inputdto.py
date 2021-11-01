"""
input defines and processes input.

This includes the map, characters, and monsters.
public classes of this file are "DTO"s, or Data Transfer Objects.
They are intended solely to convey data and contain little or
no public logic.
"""

import json
import jsonschema  # type: ignore
import logging
import pathlib
import typing

# each module/file should provide a global-level logger using this statement
logger = logging.getLogger(__name__)


class CharacterDTO(object):
    """
    Class representing a character input.

    Required input json format:
    "name" : string
    "initiative" : number 1-100 -- first card initiative
    "initiative2" : number 1-100 -- the 2nd card initiative
    "x" : number -- x coordinate
    "y" : number -- y coordinate
    """

    name: str
    initiative: int
    initiative2: int
    x: int
    y: int

    def __init__(self, dct: dict[str, typing.Any]) -> None:
        """Validate and construct the character."""
        self.name = dct['name']
        self.initiative = dct['initiative']
        self.initiative2 = dct['initiative2']
        if self.initiative2 < self.initiative:
            raise ValueError(
                ("initiative must be less than or "
                 "equal to initiative2: {} {}").format(
                    self.initiative, self.initiative2))
        self.x = dct['x']
        self.y = dct['y']

    def json_default(self) -> typing.Any:
        """Override json serialization via __init__.py monkey patch."""
        return {
            "name": self.name,
            "initiative": self.initiative,
            "initiative2": self.initiative2,
            "x": self.x,
            "y": self.y,
        }

    def __str__(self) -> str:
        """Return a string for the object."""
        return json.dumps(self)


class MonsterDTO(object):
    """
    Class representing a monster input.

    Required input json format:
    "name" : string
    "number" : number -- placard number
    "initiative" : number 1-100 -- initiative
    "x" : number -- x coordinate
    "y" : number -- y coordinate
    """

    name: str
    number: int
    initiative: int
    x: int
    y: int

    def __init__(self, dct: dict[str, typing.Any]) -> None:
        """Validate and construct the monster."""
        self.name = dct['name']
        self.number = dct['number']
        self.initiative = dct['initiative']
        self.x = dct['x']
        self.y = dct['y']

    def json_default(self) -> typing.Any:
        """Override json serialization via __init__.py monkey patch."""
        return {
            "name": self.name,
            "number": self.number,
            "initiative": self.initiative,
            "x": self.x,
            "y": self.y,
        }

    def __str__(self) -> str:
        """Return a string for the object."""
        return json.dumps(self)


class InputDTO(object):
    """
    Class representing the user input.

    Required input json format:
    "characters" : [<characters>] -- list of characters
    "monsters" : [<monsters>] -- list of monsters
    "mm_name" : string -- moving monster name
    "mm_num" : number -- moving monster placard number
    """

    # raw parsed json for reference
    _dct: dict[str, object]

    # component data
    characters: list[CharacterDTO]
    monsters: list[MonsterDTO]
    mm_name: str
    mm_num: int

    def __init__(self, dct: dict[str, typing.Any]) -> None:
        """Validate and construct Input."""
        self._dct = dct

        self.characters = []
        for c in dct["characters"]:
            self.characters.append(CharacterDTO(c))

        self.monsters = []
        for m in dct["monsters"]:
            self.monsters.append(MonsterDTO(m))

        self.mm_name = dct["mm_name"]
        self.mm_num = dct["mm_num"]

        # perform value validation
        self._assert_unique_character_names()
        self._assert_unique_monster_labels()
        self._assert_distinct_object_locations()

    def _assert_unique_character_names(self) -> None:
        """Assert all characters have unique names."""
        character_names: set[str] = set()
        for c in self.characters:
            name: str = c.name
            if name in character_names:
                raise ValueError("duplicate character name: {}".format(name))
            character_names.add(name)

    def _assert_unique_monster_labels(self) -> None:
        """Assert all monsters have unique (name, number)."""
        monster_labels: set[tuple[str, int]] = set()
        for m in self.monsters:
            monster_name: str = m.name
            number: int = m.number
            label: tuple[str, int] = (monster_name, number,)
            if label in monster_labels:
                raise ValueError("duplicate monster label: {}".format(label))
            monster_labels.add(label)

    def _assert_distinct_object_locations(self) -> None:
        """Assert that no 2 character or monster occupy the same hex."""
        location_to_object: dict[
            tuple[int, int],
            typing.Union[CharacterDTO, MonsterDTO]] = {}
        objects: list[typing.Union[CharacterDTO, MonsterDTO]] = []
        objects.extend(self.characters)
        objects.extend(self.monsters)
        for obj in objects:
            location: tuple[int, int] = (obj.x, obj.y,)
            if location in location_to_object:
                raise ValueError(
                    "two objects occupy the same hex: {}, {}".format(
                        location_to_object[location], obj))
            location_to_object[location] = obj

    def json_default(self) -> typing.Any:
        """Override json serialization via __init__.py monkey patch."""
        return {
            "characters": self.characters,
            "monsters": self.monsters,
            "mm_name": self.mm_name,
            "mm_num": self.mm_num,
        }

    def __str__(self) -> str:
        """Return a string for the object."""
        return json.dumps(self)


def decode(input_str: str) -> InputDTO:
    """Decode the input or raise an exception."""
    logger.debug("starting input decode. input: %s", input_str)
    # parse the json
    dct: dict[str, typing.Any] = json.loads(input_str)
    logger.debug("loaded json")
    return construct(dct)


def construct(input_dict: dict[str, typing.Any]) -> InputDTO:
    """Construct the input objects, validating along the way."""
    # load the schema
    logger.debug("loading input.schema.json")
    path = pathlib.Path(__file__).parent / "input.schema.json"
    with path.open() as f:
        schema_text = f.read()
    schema = json.loads(schema_text)

    # validate with schema
    logger.debug("validating input with schema")
    jsonschema.validate(input_dict, schema)
    logger.debug("input validated with schema")

    # construct the input object.  Performs additional validation
    logger.debug("constructing input DTOs")
    dto = InputDTO(input_dict)
    logger.debug("constructed final DTO: %s", dto)
    return dto
