"""Version-1 public interchange for raw observations."""

from __future__ import annotations

from typing import BinaryIO

from ..contracts.canonical_json import _encode_document
from ..contracts.errors import ContractShapeError
from ._raw_io import _read_raw_observation
from ._raw_wire import _raw_observation_wire
from .models import RawObservation

__all__ = [  # noqa: RUF022 -- canonical specification ownership order
    "load_raw_observation_v1",
    "loads_raw_observation_v1",
    "dump_raw_observation_v1",
    "dumps_raw_observation_v1",
]


def load_raw_observation_v1(binary_file: BinaryIO, *, source: str = "<memory>") -> RawObservation:
    """Read one version-1 observation from a caller-owned binary stream."""
    if not callable(getattr(binary_file, "read", None)):
        raise TypeError("expected a binary stream")
    data = binary_file.read()
    if type(data) is not bytes:
        raise TypeError("expected a binary stream")
    return loads_raw_observation_v1(data, source=source)


def loads_raw_observation_v1(data: str | bytes, *, source: str = "<memory>") -> RawObservation:
    """Read one observation from UTF-8 bytes or Unicode JSON text."""
    if type(data) not in (str, bytes):
        raise TypeError("raw observation input must be bytes or Unicode JSON text")
    return _read_raw_observation(data, source=source)


def dump_raw_observation_v1(value: RawObservation, binary_file: BinaryIO) -> None:
    """Write one canonical raw observation to a caller-owned stream."""
    if not callable(getattr(binary_file, "write", None)):
        raise TypeError("expected a binary stream")
    data = memoryview(dumps_raw_observation_v1(value))
    offset = 0
    while offset < len(data):
        count = binary_file.write(data[offset:])
        if count is None or (type(count) is int and count == 0):
            raise BlockingIOError("binary stream made no write progress")
        if type(count) is not int or count < 0 or count > len(data) - offset:
            raise OSError("binary stream returned an invalid write count")
        offset += count


def dumps_raw_observation_v1(value: RawObservation) -> bytes:
    """Serialize an owned raw observation as canonical UTF-8 with its final LF."""
    if type(value) is not RawObservation:
        raise ContractShapeError("expected an owned raw observation", path="")
    return _encode_document(_raw_observation_wire(value))
