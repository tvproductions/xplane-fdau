"""Owned catalog projection and canonical identity composition."""

from __future__ import annotations

import re
from collections.abc import Mapping
from typing import Any, cast

from ..contracts._content_hash import _record_content_hash
from ..contracts._json_parse import _NumberToken, _ObjectPairs
from ..contracts.canonical_json import _encode_document
from ..contracts.errors import ContractHashError, ContractShapeError, UnsupportedContractVersionError
from ..contracts.provenance import Authority, ProvenanceSource
from ..contracts.values import _OMITTED, _scalar_check
from ..measurements._definition_io import _plain as _metadata_plain
from ._catalog_validation import _FAMILY, _ORDER, _validate_catalog_fields
from ._definition_io import _binding_domain_tree, _binding_entry_build, _binding_entry_hash, _plain
from .models import SourceBindingCatalog, _catalog_fields


def _source_binding_catalog_wire(value: SourceBindingCatalog, *, include_hash: bool = True) -> dict[str, object]:
    fields = _catalog_fields(value)
    if include_hash:
        fields["content_hash"] = value.content_hash
    return fields


def _source_binding_catalog_bytes(value: SourceBindingCatalog) -> bytes:
    return _encode_document(_source_binding_catalog_wire(value))


def _root_fields(raw: object) -> dict[str, object]:
    if isinstance(raw, _ObjectPairs):
        return dict(raw.pairs)
    if type(raw) is dict:
        return cast(dict[str, object], raw)
    if raw is None:
        from ..contracts.errors import CanonicalJSONError

        raise CanonicalJSONError("null is prohibited", path="")
    raise ContractShapeError("expected catalog object", path="")


def _catalog_envelope(raw: object) -> None:
    fields = _root_fields(raw)
    for name, domain in (("contract_family", "string"), ("schema_version", "integer")):
        if name not in fields:
            raise ContractShapeError("missing envelope property", path=f"/{name}")
        value = fields[name]
        shadow = 0.0 if isinstance(value, _NumberToken) and value.is_real else 0 if isinstance(value, _NumberToken) else value
        _scalar_check(shadow, domain, 0, path=f"/{name}")
        # Null belongs to the later canonical-domain tier.
        if value is None:
            continue
        expected = _FAMILY if name == "contract_family" else 1
        comparison = value.text if isinstance(value, _NumberToken) else value
        if comparison != (str(expected) if isinstance(value, _NumberToken) else expected):
            raise UnsupportedContractVersionError("unsupported contract family or version", path=f"/{name}")


def _catalog_shape(raw: object) -> dict[str, object]:
    source = _root_fields(raw)
    fields: dict[str, object] = {}
    # Preserve semantic order independently of input object-member order.
    for name in (*_ORDER, *(key for key in source if key not in _ORDER)):
        if name not in source:
            continue
        value = source[name]
        if name == "definitions" and type(value) in (list, tuple):
            fields[name] = tuple(_plain(entry) for entry in cast(list[object], value))
        else:
            fields[name] = _metadata_plain(value, stem=name)
    shadow = cast(dict[str, object], _plain(fields, tokens=False))
    _validate_catalog_fields(shadow, 0, wire=True)
    return fields


def _catalog_domains(fields: Mapping[str, object]) -> dict[str, object]:
    result = cast(dict[str, object], _binding_domain_tree(dict(fields), path=""))
    _validate_catalog_fields(result, 1, wire=True)
    return result


def _catalog_hashes(fields: Mapping[str, object]) -> None:
    for index, entry in enumerate(cast(tuple[Mapping[str, object], ...], fields["definitions"])):
        _binding_entry_hash(entry, path=f"/definitions/{index}")
    declared = fields["content_hash"]
    if type(declared) is str and re.fullmatch(r"[0-9a-f]{64}", declared) is not None:
        actual = _record_content_hash({name: value for name, value in fields.items() if name != "content_hash"})
        if actual != declared:
            raise ContractHashError("declared catalog hash differs from computed hash", path="/content_hash")


def _catalog_semantics(fields: Mapping[str, object]) -> None:
    _validate_catalog_fields(fields, 2, wire=True)


def _catalog_build(fields: Mapping[str, object]) -> SourceBindingCatalog:
    f = cast(Mapping[str, Any], fields)
    authority = f["authority"]
    return SourceBindingCatalog(
        contract_family=f["contract_family"],
        schema_version=f["schema_version"],
        catalog_id=f["catalog_id"],
        catalog_revision=f["catalog_revision"],
        authority=Authority(authority_id=authority["authority_id"], authority_revision=authority["authority_revision"]),
        provenance=tuple(
            ProvenanceSource(
                source_id=p["source_id"],
                scope=p["scope"],
                source_revision=p.get("source_revision"),
                source_version=p.get("source_version"),
                locator=p.get("locator"),
                sha256=p.get("sha256"),
            )
            for p in f["provenance"]
        ),
        definitions=tuple(_binding_entry_build(entry) for entry in f["definitions"]),
        title=f.get("title", _OMITTED),
        scope=f.get("scope", _OMITTED),
    )


def _catalog_identity(raw: object, path: str) -> str | None:
    """Extract bounded scalar identity only, without materializing the document."""
    fields = dict(raw.pairs) if isinstance(raw, _ObjectPairs) else raw
    if type(fields) is not dict:
        return None
    fields = cast(dict[str, object], fields)
    tokens = path.split("/")
    name = "catalog_id"
    entries = fields.get("definitions")
    if len(tokens) >= 3 and tokens[1] == "definitions" and tokens[2].isdigit() and type(entries) in (list, tuple):
        index = int(tokens[2])
        if index < len(cast(list[object], entries)):
            entry = cast(list[object], entries)[index]
            selected = dict(entry.pairs) if isinstance(entry, _ObjectPairs) else entry
            if type(selected) is dict:
                fields = cast(dict[str, object], selected)
                name = "definition_id"
    identity = fields.get(name)
    return identity[:160] if type(identity) is str else None
