"""Owned catalog projection and canonical identity composition."""

from __future__ import annotations

from ..contracts.canonical_json import _encode_document
from .models import MeasurementCatalog, _catalog_fields


def _measurement_catalog_wire(value: MeasurementCatalog, *, include_hash: bool = True) -> dict[str, object]:
    fields = _catalog_fields(value)
    if include_hash:
        fields["content_hash"] = value.content_hash
    return fields


def _measurement_catalog_bytes(value: MeasurementCatalog) -> bytes:
    return _encode_document(_measurement_catalog_wire(value))
