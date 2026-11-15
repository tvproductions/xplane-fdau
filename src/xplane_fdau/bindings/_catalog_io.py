"""Owned binding catalog projection and canonical identity composition."""

from __future__ import annotations

from ..contracts.canonical_json import _encode_document
from .models import SourceBindingCatalog, _catalog_fields


def _source_binding_catalog_wire(value: SourceBindingCatalog, *, include_hash: bool = True) -> dict[str, object]:
    fields = _catalog_fields(value)
    if include_hash:
        fields["content_hash"] = value.content_hash
    return fields


def _source_binding_catalog_bytes(value: SourceBindingCatalog) -> bytes:
    return _encode_document(_source_binding_catalog_wire(value))
