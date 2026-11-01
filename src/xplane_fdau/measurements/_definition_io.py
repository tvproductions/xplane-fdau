"""Private staged measurement-definition entry IO; no catalog authorization."""

from __future__ import annotations

import math
import re
from collections.abc import Mapping
from typing import Any, cast

from ..contracts._content_hash import _definition_content_hash
from ..contracts._identity_validation import _identifier, _integer_domain, _revision, _sha256, _text
from ..contracts._json_parse import _check_duplicates, _materialize_number, _NumberToken, _ObjectPairs, _pointer
from ..contracts.canonical_json import _encode_document
from ..contracts.errors import CanonicalJSONError, ContractHashError, ContractShapeError, FDAUContractError
from ..contracts.provenance import Authority, ProvenanceSource
from ..contracts.values import _OMITTED, PayloadSpec, RepresentationSpec, UnitSpec, _scalar_check
from ._definition_validation import _DEFINITION_ORDER, _DEFINITION_REQUIRED, _fields, _required, _validate_definition_fields
from .models import (
    ApplicabilitySelector,
    AxisSpec,
    CoordinateSpec,
    EnumerationMember,
    EnumerationSpec,
    FreshnessSpec,
    MeasurementDefinition,
    NumericSpec,
    _definition_fields,
)

_CONTRACT_FAMILY = "https://tvproductions.github.io/xplane-fdau/contracts/measurement-catalog"
_ORDERS = {
    "definition": (*_DEFINITION_ORDER[:2], "content_hash", *_DEFINITION_ORDER[2:]),
    "authority": ("authority_id", "authority_revision"),
    "provenance": ("source_id", "scope", "source_revision", "source_version", "locator", "sha256"),
    "representation": ("kind", "element_representation", "length", "minimum_length", "maximum_length", "payload"),
    "payload": ("allowed_media_types", "allowed_storage_roles"),
    "unit": ("kind", "quantity_id", "unit_id"),
    "coordinates": ("kind", "reference_frame_id", "datum_id", "handedness", "axes"),
    "axes": ("axis_id", "direction", "sign_convention"),
    "numeric": ("storage_precision_bits", "resolution", "minimum", "maximum"),
    "enumeration": ("members",),
    "members": ("code", "label", "kind"),
    "freshness": ("fresh_for_ns", "stale_after_ns"),
    "applicability": ("class_id", "value"),
}


def _axis_spec_wire(value: AxisSpec) -> dict[str, object]:
    return dict(axis_id=value.axis_id, direction=value.direction, sign_convention=value.sign_convention)


def _coordinate_spec_wire(value: CoordinateSpec) -> dict[str, object]:
    result: dict[str, object] = {"kind": value.kind}
    for name, child in (("reference_frame_id", value.reference_frame_id), ("datum_id", value.datum_id), ("handedness", value.handedness)):
        if child is not _OMITTED:
            result[name] = child
    if value.axes is not _OMITTED:
        result["axes"] = [_axis_spec_wire(axis) for axis in cast(tuple[AxisSpec, ...], value.axes)]
    return result


def _numeric_spec_wire(value: NumericSpec) -> dict[str, object]:
    result: dict[str, object] = dict(storage_precision_bits=value.storage_precision_bits, resolution=value.resolution)
    for name, child in (("minimum", value.minimum), ("maximum", value.maximum)):
        if child is not _OMITTED:
            result[name] = child
    return result


def _enumeration_member_wire(value: EnumerationMember) -> dict[str, object]:
    return dict(code=value.code, label=value.label, kind=str(value.kind))


def _enumeration_spec_wire(value: EnumerationSpec) -> dict[str, object]:
    return {"members": [_enumeration_member_wire(member) for member in cast(tuple[EnumerationMember, ...], value.members)]}


def _freshness_spec_wire(value: FreshnessSpec) -> dict[str, object]:
    return {name: child for name, child in (("fresh_for_ns", value.fresh_for_ns), ("stale_after_ns", value.stale_after_ns)) if child is not _OMITTED}


def _applicability_selector_wire(value: ApplicabilitySelector) -> dict[str, object]:
    return dict(class_id=value.class_id, value=value.value)


def _measurement_definition_wire(value: MeasurementDefinition, *, include_hash: bool = True) -> dict[str, object]:
    fields = _definition_fields(value)
    fields["coordinates"] = _coordinate_spec_wire(value.coordinates)
    fields["freshness"] = _freshness_spec_wire(value.freshness)
    fields["applicability"] = [_applicability_selector_wire(item) for item in value.applicability]
    fields["interpolation_policy"] = str(value.interpolation_policy)
    fields["discontinuity_policy"] = str(value.discontinuity_policy)
    fields["sensitivity"] = str(value.sensitivity)
    fields["allowed_validity"] = [str(item) for item in value.allowed_validity]
    fields["allowed_quality"] = [str(item) for item in value.allowed_quality]
    if type(value.numeric) is NumericSpec:
        fields["numeric"] = _numeric_spec_wire(value.numeric)
    if type(value.enumeration) is EnumerationSpec:
        fields["enumeration"] = _enumeration_spec_wire(value.enumeration)
    if include_hash:
        fields["content_hash"] = value.content_hash
    return fields


def _measurement_definition_bytes(value: MeasurementDefinition) -> bytes:
    return _encode_document(_measurement_definition_wire(value))


def _plain(value: object, *, stem: str = "definition", tokens: bool = True) -> object:
    """Project with an explicit stack, retaining tokens until the domain tier.

    Rejected subtrees may be deeper than the contract limit. Copying them must
    not raise a Python recursion failure before whole-entry shape validation.
    """
    pending: list[tuple[object, str, bool]] = [(value, stem, False)]
    projected: list[object] = []
    while pending:
        current, current_stem, expanded = pending.pop()
        if isinstance(current, _NumberToken):
            projected.append(current if tokens else 0.0 if current.is_real else 0)
            continue
        if isinstance(current, _ObjectPairs):
            current = dict(current.pairs)
        if type(current) is dict:
            fields = cast(dict[str, object], current)
            order = _ORDERS.get(current_stem, ())
            names = (*[name for name in order if name in fields], *[name for name in fields if name not in order])
            if not expanded:
                pending.append((fields, current_stem, True))
                pending.extend((fields[name], name, False) for name in reversed(names))
                continue
            children = projected[-len(names) :] if names else []
            if names:
                del projected[-len(names) :]
            projected.append(dict(zip(names, children, strict=True)))
        elif type(current) in (list, tuple):
            items = cast(list[object] | tuple[object, ...], current)
            if not expanded:
                pending.append((items, current_stem, True))
                pending.extend((item, current_stem, False) for item in reversed(items))
                continue
            children = projected[-len(items) :] if items else []
            if items:
                del projected[-len(items) :]
            projected.append(tuple(children))
        elif not tokens and current is not None and type(current) not in (str, int, float, bool):
            projected.append(object())  # not an exact JSON primitive or container
        else:
            projected.append(current)
    return projected[0]


def _without_hash(fields: Mapping[str, object]) -> dict[str, object]:
    return {name: value for name, value in fields.items() if name != "content_hash"}


def _definition_entry_shape(value: object, *, path: str = "") -> dict[str, object]:
    if not isinstance(value, _ObjectPairs) and type(value) is not dict:
        raise ContractShapeError("expected definition entry object", path=path)
    fields = cast(dict[str, object], _plain(value))
    shadow = cast(dict[str, object], _plain(fields, tokens=False))
    _fields(shadow, (*_DEFINITION_REQUIRED, "content_hash"), ("numeric", "enumeration"), path=path)
    # The self-hash sits between identity and authority in semantic order.
    for name, domain in (("definition_id", "string"), ("definition_revision", "integer"), ("content_hash", "string")):
        _scalar_check(_required(shadow, name, path=path), domain, 0, path=f"{path}/{name}")
    _validate_definition_fields(_without_hash(shadow), 0, path=path)
    return fields


def _domain_tree(value: object, *, path: str, depth: int = 1) -> object:
    if isinstance(value, _NumberToken):
        return _materialize_number(value, path=path)
    if type(value) is dict:
        fields = cast(dict[str, object], value)
        if depth > 64:
            raise CanonicalJSONError("JSON nesting depth exceeded", path=path)
        if len(fields) > 65535:
            raise CanonicalJSONError("object member limit exceeded", path=path)
        result: dict[str, object] = {}
        for name, child in fields.items():
            _text(name, path=path)
            child_path = _pointer(path, name)
            result[name] = _domain_tree(child, path=child_path, depth=depth + 1)
        return result
    if type(value) in (list, tuple):
        items = cast(list[object] | tuple[object, ...], value)
        if depth > 64:
            raise CanonicalJSONError("JSON nesting depth exceeded", path=path)
        if len(items) > 65535:
            raise CanonicalJSONError("array member limit exceeded", path=path)
        return tuple(_domain_tree(child, path=f"{path}/{index}", depth=depth + 1) for index, child in enumerate(items))
    if value is None:
        raise CanonicalJSONError("null is prohibited", path=path)
    if type(value) is str:
        _text(value, path=path)
    elif type(value) is int:
        _integer_domain(value, path=path)
    elif type(value) is float and not math.isfinite(value):
        raise CanonicalJSONError("nonfinite binary64", path=path)
    return value


def _definition_entry_domains(fields: Mapping[str, object], *, path: str = "") -> dict[str, object]:
    result = cast(dict[str, object], _domain_tree(_plain(dict(fields)), path=path))
    _validate_definition_fields(_without_hash(result), 1, path=path)
    return result


def _definition_entry_hash(fields: Mapping[str, object], *, path: str = "") -> None:
    declared = fields["content_hash"]
    if type(declared) is str and re.fullmatch(r"[0-9a-f]{64}", declared) is not None:
        # The preimage helper never sees the declared hash's syntax.
        actual = _definition_content_hash(_CONTRACT_FAMILY, _without_hash(fields))
        if actual != declared:
            raise ContractHashError("declared definition hash differs from computed hash", path=f"{path}/content_hash")


def _definition_entry_semantics(fields: Mapping[str, object], *, path: str = "") -> None:
    # Repeat just the two earlier identity checks to preserve the declared hash's
    # specified position without changing the shared constructor validator.
    _identifier(fields["definition_id"], path=f"{path}/definition_id")
    _revision(fields["definition_revision"], path=f"{path}/definition_revision")
    _sha256(fields["content_hash"], path=f"{path}/content_hash")
    _validate_definition_fields(_without_hash(fields), 2, path=path)


def _definition_entry_build(fields: Mapping[str, object]) -> MeasurementDefinition:
    """Explicit named construction after every plain-field stage succeeds."""
    f = cast(Mapping[str, Any], fields)
    authority = f["authority"]
    rep = f["representation"]
    payload = rep.get("payload")
    representation = RepresentationSpec(
        kind=rep["kind"],
        element_representation=rep.get("element_representation", _OMITTED),
        length=rep.get("length", _OMITTED),
        minimum_length=rep.get("minimum_length", _OMITTED),
        maximum_length=rep.get("maximum_length", _OMITTED),
        payload=PayloadSpec(allowed_media_types=payload["allowed_media_types"], allowed_storage_roles=payload["allowed_storage_roles"])
        if payload is not None
        else _OMITTED,
    )
    unit = f["unit"]
    coordinates = f["coordinates"]
    axes = coordinates.get("axes")
    numeric = f.get("numeric")
    enumeration = f.get("enumeration")
    freshness = f["freshness"]
    return MeasurementDefinition(
        definition_id=f["definition_id"],
        definition_revision=f["definition_revision"],
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
        title=f["title"],
        description=f["description"],
        limitations=f["limitations"],
        quantity_id=f["quantity_id"],
        representation=representation,
        unit=UnitSpec(kind=unit["kind"], quantity_id=unit.get("quantity_id", _OMITTED), unit_id=unit.get("unit_id", _OMITTED)),
        coordinates=CoordinateSpec(
            kind=coordinates["kind"],
            reference_frame_id=coordinates.get("reference_frame_id", _OMITTED),
            datum_id=coordinates.get("datum_id", _OMITTED),
            handedness=coordinates.get("handedness", _OMITTED),
            axes=tuple(AxisSpec(axis_id=a["axis_id"], direction=a["direction"], sign_convention=a["sign_convention"]) for a in axes)
            if axes is not None
            else _OMITTED,
        ),
        numeric=NumericSpec(
            storage_precision_bits=numeric["storage_precision_bits"],
            resolution=numeric["resolution"],
            minimum=numeric.get("minimum", _OMITTED),
            maximum=numeric.get("maximum", _OMITTED),
        )
        if numeric is not None
        else _OMITTED,
        enumeration=EnumerationSpec(members=tuple(EnumerationMember(code=m["code"], label=m["label"], kind=m["kind"]) for m in enumeration["members"]))
        if enumeration is not None
        else _OMITTED,
        freshness=FreshnessSpec(fresh_for_ns=freshness.get("fresh_for_ns", _OMITTED), stale_after_ns=freshness.get("stale_after_ns", _OMITTED)),
        interpolation_policy=f["interpolation_policy"],
        discontinuity_policy=f["discontinuity_policy"],
        allowed_validity=f["allowed_validity"],
        allowed_quality=f["allowed_quality"],
        sensitivity=f["sensitivity"],
        applicability=tuple(ApplicabilitySelector(class_id=a["class_id"], value=a["value"]) for a in f["applicability"]),
    )


def _duplicates(value: object, *, path: str = "") -> None:
    # Duplicate precedence requires scanning arbitrary rejected subtrees too;
    # do not impose the later canonical depth limit or use Python recursion.
    pending: list[tuple[object, str]] = [(value, path)]
    while pending:
        current, current_path = pending.pop()
        if isinstance(current, _ObjectPairs):
            _check_duplicates(_ObjectPairs(tuple((name, None) for name, _ in current.pairs)), source="<memory>", path=current_path)
            pending.extend((child, _pointer(current_path, name)) for name, child in reversed(current.pairs))
        elif type(current) is dict:
            members = cast(dict[str, object], current)
            pending.extend((child, _pointer(current_path, str(name))) for name, child in reversed(tuple(members.items())))
        elif type(current) in (list, tuple):
            items = cast(list[object] | tuple[object, ...], current)
            pending.extend((items[index], f"{current_path}/{index}") for index in range(len(items) - 1, -1, -1))


def _measurement_definition_from_wire(value: object, *, path: str = "", source: str = "<memory>") -> MeasurementDefinition:
    identity: str | None = None
    try:
        raw = dict(value.pairs) if isinstance(value, _ObjectPairs) else value
        if type(raw) is dict:
            raw_identity = cast(dict[str, object], raw).get("definition_id")
            if type(raw_identity) is str:
                identity = raw_identity[:160]
        _duplicates(value)
        fields = _definition_entry_shape(value)
        fields = _definition_entry_domains(fields)
        _definition_entry_hash(fields)
        _definition_entry_semantics(fields)
        return _definition_entry_build(fields)
    except FDAUContractError as error:
        raise type(error)(
            str(error), source=source, path=path + error.path, line=error.line, column=error.column, contract_family=_CONTRACT_FAMILY, identity=identity
        ) from None
