"""Private phased checks for plain measurement semantic field mappings."""

from __future__ import annotations

from collections.abc import Mapping
from typing import cast

from ..contracts._identity_validation import _counter, _identifier, _nfc_text
from ..contracts.errors import CanonicalJSONError, ContractShapeError, ContractValidationError
from ..contracts.values import _choice, _ordered_array, _scalar_check, _tag


def _fields(fields: Mapping[str, object], required: tuple[str, ...], optional: tuple[str, ...], *, path: str) -> None:
    if not isinstance(fields, Mapping):
        raise ContractShapeError("expected field mapping", path=path)
    for name in fields:
        if type(name) is not str:
            raise ContractShapeError("property name must be text", path=path)
        if name not in required + optional:
            token = name.replace("~", "~0").replace("/", "~1")
            raise ContractShapeError("unknown or irrelevant property", path=f"{path}/{token}")


def _required(fields: Mapping[str, object], name: str, *, path: str) -> object:
    if name not in fields:
        raise ContractShapeError("missing property", path=f"{path}/{name}")
    return fields[name]


def _null(value: object, phase: int, *, path: str) -> bool:
    if value is not None:
        return False
    if phase > 0:
        raise CanonicalJSONError("null is prohibited", path=path)
    return True


def _text_field(value: object, phase: int, *, path: str, maximum: int | None = None) -> None:
    _scalar_check(value, "string", min(phase, 1), path=path)
    if phase == 2:
        if maximum is None:
            _identifier(value, path=path)
        else:
            _nfc_text(value, path=path, maximum=maximum)


def _validate_axis_fields(fields: Mapping[str, object], phase: int, *, path: str = "") -> None:
    _fields(fields, ("axis_id", "direction", "sign_convention"), (), path=path)
    for name, maximum in (("axis_id", None), ("direction", 256), ("sign_convention", 512)):
        _text_field(_required(fields, name, path=path), phase, path=f"{path}/{name}", maximum=maximum)


def _coordinate_header(fields: Mapping[str, object], phase: int, *, path: str = "") -> bool:
    """Check variant and preceding scalar fields before visiting owned axes."""
    _fields(fields, ("kind",), ("reference_frame_id", "datum_id", "handedness", "axes"), path=path)
    kind = _required(fields, "kind", path=path)
    if not _null(kind, phase, path=f"{path}/kind"):
        kind = _choice(kind, ("not_applicable", "applicable"), path=f"{path}/kind")
    for name in ("reference_frame_id", "datum_id", "handedness", "axes"):
        if kind == "not_applicable" and name in fields:
            raise ContractShapeError("irrelevant coordinate property", path=f"{path}/{name}")
        if kind == "applicable" and name != "datum_id" and name not in fields:
            raise ContractShapeError("missing coordinate property", path=f"{path}/{name}")
        if name not in fields or name == "axes":
            continue
        value = fields[name]
        if name == "handedness":
            if not _null(value, phase, path=f"{path}/{name}"):
                _choice(value, ("left", "right"), path=f"{path}/{name}")
        else:
            _text_field(value, phase, path=f"{path}/{name}")
    return kind == "applicable" or (kind is None and "axes" in fields)


def _validate_coordinates_fields(fields: Mapping[str, object], phase: int, *, path: str = "") -> None:
    if not _coordinate_header(fields, phase, path=path):
        return
    value = fields["axes"]
    axes_path = f"{path}/axes"
    if _null(value, phase, path=axes_path):
        return
    axes = _ordered_array(value, path=axes_path)
    if len(axes) > 32:
        raise ContractShapeError("axis count exceeds shape limit", path=axes_path)
    if phase == 2 and not axes:
        raise ContractValidationError("coordinate axes must be nonempty", path=axes_path)
    identifiers: set[object] = set()
    for index, axis in enumerate(axes):
        item_path = f"{axes_path}/{index}"
        if _null(axis, phase, path=item_path):
            continue
        if phase == 2:
            axis_fields = cast(Mapping[str, object], axis)
            _fields(axis_fields, ("axis_id", "direction", "sign_convention"), (), path=item_path)
            axis_id = _identifier(_required(axis_fields, "axis_id", path=item_path), path=f"{item_path}/axis_id")
            if axis_id in identifiers:
                raise ContractValidationError("duplicate axis identity", path=f"{item_path}/axis_id")
            identifiers.add(axis_id)
        _validate_axis_fields(cast(Mapping[str, object], axis), phase, path=item_path)


def _validate_numeric_fields(fields: Mapping[str, object], phase: int, *, path: str = "") -> None:
    _fields(fields, ("storage_precision_bits", "resolution"), ("minimum", "maximum"), path=path)
    _scalar_check(_required(fields, "storage_precision_bits", path=path), "integer", min(phase, 1), path=f"{path}/storage_precision_bits")
    if phase == 2:
        precision = _counter(fields["storage_precision_bits"], path=f"{path}/storage_precision_bits")
        if not 1 <= precision <= 64:
            raise ContractValidationError("storage precision outside range", path=f"{path}/storage_precision_bits")
    resolution = _required(fields, "resolution", path=path)
    domain = "real" if type(resolution) is float else "integer"
    for name in ("resolution", "minimum", "maximum"):
        if name not in fields:
            continue
        value = fields[name]
        _scalar_check(value, domain, min(phase, 1), path=f"{path}/{name}")
        if phase == 2 and name == "resolution" and cast(int | float, value) <= 0:
            raise ContractValidationError("resolution must be positive", path=f"{path}/resolution")
    if phase == 2 and "minimum" in fields and "maximum" in fields and cast(int | float, fields["minimum"]) > cast(int | float, fields["maximum"]):
        raise ContractValidationError("maximum below minimum", path=f"{path}/maximum")


def _validate_enumeration_member_fields(fields: Mapping[str, object], phase: int, *, path: str = "") -> None:
    from .models import EnumerationMemberKind

    _fields(fields, ("code", "label", "kind"), (), path=path)
    _text_field(_required(fields, "code", path=path), phase, path=f"{path}/code")
    _text_field(_required(fields, "label", path=path), phase, path=f"{path}/label", maximum=256)
    value = _required(fields, "kind", path=path)
    if not _null(value, phase, path=f"{path}/kind"):
        _tag(value, EnumerationMemberKind, path=f"{path}/kind")


def _validate_enumeration_fields(fields: Mapping[str, object], phase: int, *, path: str = "") -> None:
    _fields(fields, ("members",), (), path=path)
    value = _required(fields, "members", path=path)
    members_path = f"{path}/members"
    if _null(value, phase, path=members_path):
        return
    members = _ordered_array(value, path=members_path)
    if phase == 2 and not members:
        raise ContractValidationError("enumeration members must be nonempty", path=members_path)
    previous: str | None = None
    unknown = False
    for index, member in enumerate(members):
        item_path = f"{members_path}/{index}"
        if _null(member, phase, path=item_path):
            continue
        checked = cast(Mapping[str, object], member)
        if phase == 2:
            _fields(checked, ("code", "label", "kind"), (), path=item_path)
            code = _identifier(_required(checked, "code", path=item_path), path=f"{item_path}/code")
            if previous is not None and previous >= code:
                raise ContractValidationError("member codes must be unique and ordered", path=f"{item_path}/code")
            previous = code
        _validate_enumeration_member_fields(checked, phase, path=item_path)
        if phase == 2 and checked["kind"] == "unknown":
            if unknown:
                raise ContractValidationError("multiple unknown members", path=f"{item_path}/kind")
            unknown = True


def _validate_freshness_fields(fields: Mapping[str, object], phase: int, *, path: str = "") -> None:
    _fields(fields, (), ("fresh_for_ns", "stale_after_ns"), path=path)
    if not fields:
        raise ContractShapeError("at least one freshness limit is required", path=f"{path}/fresh_for_ns")
    for name in ("fresh_for_ns", "stale_after_ns"):
        if name in fields:
            _scalar_check(fields[name], "integer", min(phase, 1), path=f"{path}/{name}")
            if phase == 2:
                _counter(fields[name], path=f"{path}/{name}")
    if phase == 2 and "fresh_for_ns" in fields and "stale_after_ns" in fields and cast(int, fields["fresh_for_ns"]) > cast(int, fields["stale_after_ns"]):
        raise ContractValidationError("stale limit precedes fresh limit", path=f"{path}/stale_after_ns")


def _validate_applicability_fields(fields: Mapping[str, object], phase: int, *, path: str = "") -> None:
    _fields(fields, ("class_id", "value"), (), path=path)
    _text_field(_required(fields, "class_id", path=path), phase, path=f"{path}/class_id")
    _text_field(_required(fields, "value", path=path), phase, path=f"{path}/value", maximum=256)
