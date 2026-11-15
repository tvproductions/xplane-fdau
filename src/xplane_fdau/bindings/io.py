"""Explicit version-1 source_binding catalog binary interchange."""

from __future__ import annotations

from typing import BinaryIO

from ..contracts._json_parse import _parse_json_document
from ..contracts.errors import ContractShapeError, FDAUContractError
from ._catalog_io import (
    _catalog_build,
    _catalog_domains,
    _catalog_envelope,
    _catalog_hashes,
    _catalog_identity,
    _catalog_semantics,
    _catalog_shape,
    _source_binding_catalog_bytes,
)
from ._catalog_validation import _FAMILY
from .models import SourceBindingCatalog

__all__ = [  # noqa: RUF022 -- specified load/loads/dump/dumps ownership order
    "load_source_binding_catalog_v1",
    "loads_source_binding_catalog_v1",
    "dump_source_binding_catalog_v1",
    "dumps_source_binding_catalog_v1",
]


def loads_source_binding_catalog_v1(data: str | bytes, *, source: str = "<memory>") -> SourceBindingCatalog:
    """Load exactly family version 1, validating the complete document before construction."""
    if type(data) not in (str, bytes):
        raise TypeError("catalog input must be bytes or Unicode JSON text")
    raw: object = None
    try:
        raw = _parse_json_document(data, source=source)
        _catalog_envelope(raw)
        fields = _catalog_shape(raw)
        fields = _catalog_domains(fields)
        _catalog_hashes(fields)
        _catalog_semantics(fields)
        return _catalog_build(fields)
    except FDAUContractError as error:
        raise type(error)(
            str(error),
            source=source,
            line=error.line,
            column=error.column,
            path=error.path,
            contract_family=_FAMILY,
            identity=_catalog_identity(raw, error.path),
        ) from None


def load_source_binding_catalog_v1(binary_file: BinaryIO, *, source: str = "<memory>") -> SourceBindingCatalog:
    """Read a caller-owned binary stream without seeking or closing it."""
    if not hasattr(binary_file, "read"):
        raise TypeError("expected binary stream")
    data = binary_file.read()
    if type(data) is not bytes:
        raise TypeError("expected binary stream")
    return loads_source_binding_catalog_v1(data, source=source)


def dumps_source_binding_catalog_v1(value: SourceBindingCatalog) -> bytes:
    """Serialize an owned catalog to canonical UTF-8 with one final LF."""
    if type(value) is not SourceBindingCatalog:
        raise ContractShapeError("expected owned source_binding catalog", path="")
    return _source_binding_catalog_bytes(value)


def dump_source_binding_catalog_v1(value: SourceBindingCatalog, binary_file: BinaryIO) -> None:
    """Write canonical bytes, leaving ownership and I/O failures with the caller."""
    data = memoryview(dumps_source_binding_catalog_v1(value))
    offset = 0
    while offset < len(data):
        count = binary_file.write(data[offset:])
        if count is None or count == 0:
            raise BlockingIOError("binary stream made no write progress")
        if type(count) is not int or count < 0 or count > len(data) - offset:
            raise OSError("binary stream returned an invalid write count")
        offset += count
