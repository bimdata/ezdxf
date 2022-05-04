#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License
from typing import NamedTuple, Any, Sequence, List, Iterator, Union, Iterable, cast
from datetime import datetime
import struct
from ezdxf._acis.const import (
    ParsingError,
    DATE_FMT,
    Tags,
    DATA_END_MARKERS,
)
from ezdxf._acis.hdr import AcisHeader
from ezdxf._acis.abstract import AbstractEntity


class Token(NamedTuple):
    tag: int
    value: Any


SabRecord = List[Token]


class Decoder:
    def __init__(self, data: bytes):
        self.data = data
        self.index: int = 0

    @property
    def has_data(self) -> bool:
        return self.index < len(self.data)

    def read_header(self) -> AcisHeader:
        header = AcisHeader()
        signature = self.data[0:15]
        if signature != b"ACIS BinaryFile":
            raise ParsingError("not a SAB file")
        self.index = 15

        header.version = self.read_int()
        header.n_records = self.read_int()
        header.n_entities = self.read_int()
        header.flags = self.read_int()
        header.product_id = self.read_str_tag()
        header.acis_version = self.read_str_tag()
        date = self.read_str_tag()
        header.creation_date = datetime.strptime(date, DATE_FMT)
        header.units_in_mm = self.read_double_tag()
        # tolerances are ignored
        _ = self.read_double_tag()  # res_tol
        _ = self.read_double_tag()  # nor_tol
        return header

    def forward(self, count: int):
        pos = self.index
        self.index += count
        return pos

    def read_byte(self) -> int:
        pos = self.forward(1)
        return self.data[pos]

    def read_bytes(self, count: int) -> bytes:
        pos = self.forward(count)
        return self.data[pos : pos + count]

    def read_int(self) -> int:
        pos = self.forward(4)
        values = struct.unpack_from("<i", self.data, pos)[0]
        return values

    def read_float(self) -> float:
        pos = self.forward(8)
        return struct.unpack_from("<d", self.data, pos)[0]

    def read_floats(self, count: int) -> Sequence[float]:
        pos = self.forward(8 * count)
        return struct.unpack_from(f"<{count}d", self.data, pos)

    def read_str(self, length) -> str:
        text = self.read_bytes(length)
        return text.decode()

    def read_str_tag(self) -> str:
        tag = self.read_byte()
        if tag != Tags.STR:
            raise ParsingError("string tag (7) not found")
        return self.read_str(self.read_byte())

    def read_double_tag(self) -> float:
        tag = self.read_byte()
        if tag != Tags.DOUBLE:
            raise ParsingError("double tag (6) not found")
        return self.read_float()

    def read_record(self) -> SabRecord:
        def entity_name():
            return "-".join(entity_type)

        values: SabRecord = []
        entity_type: List[str] = []
        subtype_level: int = 0
        while True:
            if not self.has_data:
                if values:
                    token = values[0]
                    if token.value in DATA_END_MARKERS:
                        return values
                raise ParsingError("pre-mature end of data")
            tag = self.read_byte()
            if tag == Tags.INT:
                values.append(Token(tag, self.read_int()))
            elif tag == Tags.DOUBLE:
                values.append(Token(tag, self.read_float()))
            elif tag == Tags.STR:
                values.append(Token(tag, self.read_str(self.read_byte())))
            elif tag == Tags.POINTER:
                values.append(Token(tag, self.read_int()))
            elif tag == Tags.BOOL_FALSE:
                values.append(Token(tag, False))
            elif tag == Tags.BOOL_TRUE:
                values.append(Token(tag, True))
            elif tag == Tags.LONG_STR:
                values.append(Token(tag, self.read_str(self.read_int())))
            elif tag == Tags.ENTITY_TYPE_EX:
                entity_type.append(self.read_str(self.read_byte()))
            elif tag == Tags.ENTITY_TYPE:
                entity_type.append(self.read_str(self.read_byte()))
                values.append(Token(tag, entity_name()))
                entity_type.clear()
            elif tag == Tags.LOCATION_VEC:
                values.append(Token(tag, self.read_floats(3)))
            elif tag == Tags.DIRECTION_VEC:
                values.append(Token(tag, self.read_floats(3)))
            elif tag == Tags.UNKNOWN_0x15:
                values.append(Token(tag, self.read_int()))
            elif tag == Tags.UNKNOWN_0x17:
                values.append(Token(tag, self.read_float()))
            elif tag == Tags.SUBTYPE_START:
                subtype_level += 1
                values.append(Token(tag, subtype_level))
            elif tag == Tags.SUBTYPE_END:
                values.append(Token(tag, subtype_level))
                subtype_level -= 1
            elif tag == Tags.RECORD_END:
                return values
            else:
                raise ParsingError(
                    f"unknown SAB tag: 0x{tag:x} ({tag}) in entity '{values[0].value}'"
                )

    def read_records(self) -> Iterator[SabRecord]:
        while True:
            try:
                if self.has_data:
                    yield self.read_record()
                else:
                    return
            except IndexError:
                return


class SabEntity(AbstractEntity):
    """Low level representation of an ACIS entity (node)."""

    def __init__(
        self,
        name: str,
        attr_ptr: int = -1,
        id: int = -1,
        data: SabRecord = None,
    ):
        self.name = name
        self.attr_ptr = attr_ptr
        self.id = id
        self.data: SabRecord = data if data is not None else []
        self.attributes: "SabEntity" = None  # type: ignore

    def __str__(self):
        return f"{self.name}({self.id})"

    def find_all(self, entity_type: str) -> List["SabEntity"]:
        """Returns a list of all matching ACIS entities of then given type
        referenced by this entity.

        Args:
            entity_type: entity type (name) as string like "body"

        """
        return [
            t.value
            for t in self.data
            if isinstance(t.value, SabEntity) and t.value.name == entity_type
        ]

    def find_first(self, entity_type: str) -> "SabEntity":
        """Returns the first matching ACIS entity referenced by this entity.
        Returns the ``NULL_PTR`` if no entity was found.

        Args:
            entity_type: entity type (name) as string like "body"

        """
        for token in self.data:
            if token.tag == Tags.POINTER:
                entity = cast(SabEntity, token.value)
                if entity.name == entity_type:
                    return entity
        return NULL_PTR

    def parse_values(self, fmt: str) -> Sequence[Any]:
        """Parse only values from entity data, ignores all entities in front
        or between the data values.

        =========== ==============================
        specifier   data type
        =========== ==============================
        ``f``       float values
        ``i``       integer values
        ``s``       string constants like "forward"
        ``@``       user string with preceding length encoding
        ``?``       skip (unknown) value
        =========== ==============================

        Args:
            fmt: format specifiers separated by ";"

        """
        return tuple()


NULL_PTR = SabEntity("null-ptr", -1, -1, tuple())  # type: ignore


class SabBuilder:
    """Low level data structure to manage ACIS SAB data files."""

    def __init__(self):
        self.header = AcisHeader()
        self.bodies: List[SabEntity] = []
        self.entities: List[SabEntity] = []

    def set_entities(self, entities: List[SabEntity]) -> None:
        """Reset entities and bodies list. (internal API)"""
        self.bodies = [e for e in entities if e.name == "body"]
        self.entities = entities


def build_entities(
    records: Iterable[SabRecord], version: int
) -> Iterator[SabEntity]:
    for record in records:
        name = record[0].value
        if name in DATA_END_MARKERS:
            yield SabEntity(name)
            return
        attr = record[1].value
        id_ = -1
        if version >= 700:
            id_ = record[2].value
            data = record[3:]
        else:
            data = record[2:]
        yield SabEntity(name, attr, id_, data)


def resolve_pointers(entities: List[SabEntity]) -> List[SabEntity]:
    def ptr(num: int) -> SabEntity:
        if num == -1:
            return NULL_PTR
        return entities[num]

    for entity in entities:
        entity.attributes = ptr(entity.attr_ptr)
        entity.attr_ptr = -1
        for index, token in enumerate(entity.data):
            if token.tag == Tags.POINTER:
                entity.data[index] = Token(token.tag, ptr(token.value))
    return entities


def parse_sab(b: Union[bytes, bytearray, Sequence[bytes]]) -> SabBuilder:
    """Returns the :class:`SabBuilder` for the ACIS SAB file content given as
    string or list of strings.

    Raises:
        ParsingError: invalid or unsupported ACIS data structure

    """
    data: bytes
    if isinstance(b, (bytes, bytearray)):
        data = b
    else:
        data = b"".join(b)
    if not isinstance(data, (bytes, bytearray)):
        raise TypeError("expected bytes, bytearray or a sequence of bytes")
    builder = SabBuilder()
    decoder = Decoder(data)
    builder.header = decoder.read_header()
    entities = list(
        build_entities(decoder.read_records(), builder.header.version)
    )
    builder.set_entities(resolve_pointers(entities))
    return builder