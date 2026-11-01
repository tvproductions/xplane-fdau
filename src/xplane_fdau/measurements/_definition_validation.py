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


_DEFINITION_REQUIRED = (
    "definition_id",
    "definition_revision",
    "authority",
    "provenance",
    "title",
    "description",
    "limitations",
    "quantity_id",
    "representation",
    "unit",
    "coordinates",
    "freshness",
    "interpolation_policy",
    "discontinuity_policy",
    "allowed_validity",
    "allowed_quality",
    "sensitivity",
    "applicability",
)
_DEFINITION_ORDER = (*_DEFINITION_REQUIRED[:11], "numeric", "enumeration", *_DEFINITION_REQUIRED[11:])


def _validate_authority_fields(fields: Mapping[str, object], phase: int, *, path: str) -> None:
    from ..contracts._identity_validation import _revision

    _fields(fields, ("authority_id", "authority_revision"), (), path=path)
    _text_field(_required(fields, "authority_id", path=path), phase, path=f"{path}/authority_id")
    value = _required(fields, "authority_revision", path=path)
    _scalar_check(value, "integer", min(phase, 1), path=f"{path}/authority_revision")
    if phase == 2:
        _revision(value, path=f"{path}/authority_revision")


def _validate_provenance_fields(fields: Mapping[str, object], phase: int, *, path: str, identities: set[object]) -> None:
    from ..contracts._identity_validation import _revision, _sha256, _version_text

    _fields(fields, ("source_id", "scope"), ("source_revision", "source_version", "locator", "sha256"), path=path)
    for name, maximum in (("source_id", None), ("scope", 1024), ("source_revision", None), ("source_version", 128), ("locator", 2048), ("sha256", 64)):
        if name not in fields and name not in ("source_id", "scope"):
            continue
        value = _required(fields, name, path=path)
        child_path = f"{path}/{name}"
        if name == "source_revision":
            _scalar_check(value, "integer", min(phase, 1), path=child_path)
            if phase == 2:
                _revision(value, path=child_path)
        else:
            _text_field(value, phase, path=child_path, maximum=maximum)
            if phase == 2 and name == "source_version":
                _version_text(value, path=child_path)
            if phase == 2 and name == "sha256":
                _sha256(value, path=child_path)
        if phase == 2 and name == "scope" and "source_revision" not in fields and "source_version" not in fields:
            raise ContractValidationError("provenance requires revision or version", path=f"{path}/source_revision")
        if phase == 2 and name == "source_version" and "source_revision" in fields:
            raise ContractValidationError("provenance cannot have revision and version", path=child_path)
        if phase == 2 and ((name == "source_revision" and "source_version" not in fields) or (name == "source_version" and "source_revision" not in fields)):
            key = (fields["source_id"], name, value)
            if key in identities:
                raise ContractValidationError("duplicate provenance identity", path=path)
            identities.add(key)


def _validate_representation_fields(fields: Mapping[str, object], phase: int, *, path: str) -> None:
    from ..contracts.values import ScalarRepresentation, ValueRepresentation, _array_set_check

    inventory = ("element_representation", "length", "minimum_length", "maximum_length", "payload")
    _fields(fields, ("kind",), inventory, path=path)
    kind = _required(fields, "kind", path=path)
    if not _null(kind, phase, path=f"{path}/kind"):
        kind = _tag(kind, ValueRepresentation, path=f"{path}/kind")
    selected = {
        "vector": ("length",),
        "fixed_array": ("element_representation", "length"),
        "variable_array": ("element_representation", "minimum_length", "maximum_length"),
        "referenced_bytes": ("payload",),
    }.get(cast(str, kind), ())
    for name in inventory:
        child_path = f"{path}/{name}"
        if kind is not None:
            if name not in selected:
                if name in fields:
                    raise ContractShapeError("irrelevant representation property", path=child_path)
                continue
            value = _required(fields, name, path=path)
        elif name in fields:
            value = fields[name]
        else:
            continue
        if _null(value, phase, path=child_path):
            continue
        if name == "element_representation":
            _tag(value, ScalarRepresentation, path=child_path)
        elif name == "payload":
            payload = cast(Mapping[str, object], value)
            _fields(payload, ("allowed_media_types", "allowed_storage_roles"), (), path=child_path)
            for prop in ("allowed_media_types", "allowed_storage_roles"):
                _array_set_check(_required(payload, prop, path=child_path), phase, path=f"{child_path}/{prop}", media=prop == "allowed_media_types")
        else:
            _scalar_check(value, "integer", min(phase, 1), path=child_path)
            if phase == 2:
                length = _counter(value, path=child_path)
                if not (1 if name == "length" else 0) <= length <= (1024 if kind == "vector" else 65535):
                    raise ContractValidationError("declared length outside range", path=child_path)
                if name == "minimum_length" and length > cast(int, fields["maximum_length"]):
                    raise ContractValidationError("minimum exceeds maximum length", path=child_path)


def _validate_unit_fields(fields: Mapping[str, object], phase: int, *, path: str, definition: Mapping[str, object]) -> None:
    _fields(fields, ("kind",), ("quantity_id", "unit_id"), path=path)
    kind = _required(fields, "kind", path=path)
    if not _null(kind, phase, path=f"{path}/kind"):
        kind = _choice(kind, ("unitless", "unit"), path=f"{path}/kind")
    for name in ("quantity_id", "unit_id"):
        if kind == "unitless" and name in fields:
            raise ContractShapeError("irrelevant unit property", path=f"{path}/{name}")
        if kind == "unit" or name in fields:
            _text_field(_required(fields, name, path=path), phase, path=f"{path}/{name}")
            if phase == 2 and name == "quantity_id" and fields[name] != definition["quantity_id"]:
                raise ContractValidationError("unit quantity differs from definition", path=f"{path}/{name}")


def _definition_collection(value: object, name: str, phase: int, *, path: str) -> None:
    from .models import QualityFlag, ValidityState

    if _null(value, phase, path=path):
        return
    items = _ordered_array(value, path=path)
    if name in ("provenance", "limitations", "applicability") and len(items) > 256:
        raise ContractShapeError("collection exceeds shape limit", path=path)
    if phase == 2 and name in ("provenance", "allowed_validity") and not items:
        raise ContractValidationError("collection must be nonempty", path=path)
    seen: set[object] = set()
    previous: str | None = None
    for index, item in enumerate(items):
        child_path = f"{path}/{index}"
        if _null(item, phase, path=child_path):
            continue
        key: object = item
        if name == "limitations":
            _text_field(item, phase, path=child_path, maximum=1024)
        elif name in ("allowed_validity", "allowed_quality"):
            key = _tag(item, ValidityState if name == "allowed_validity" else QualityFlag, path=child_path)
        else:
            fields = cast(Mapping[str, object], item)
            if name == "provenance":
                _validate_provenance_fields(fields, phase, path=child_path, identities=seen)
            else:
                if phase == 2:
                    # Identity ordering is checked at class_id before the later value.
                    _fields(fields, ("class_id", "value"), (), path=child_path)
                    class_id = _identifier(_required(fields, "class_id", path=child_path), path=f"{child_path}/class_id")
                    if previous is not None and previous >= class_id:
                        raise ContractValidationError("applicability classes must be unique and ordered", path=f"{child_path}/class_id")
                    previous = class_id
                _validate_applicability_fields(fields, phase, path=child_path)
        if phase == 2 and name not in ("applicability", "provenance"):
            if key in seen:
                raise ContractValidationError("duplicate collection item", path=child_path)
            seen.add(key)
            if name in ("allowed_validity", "allowed_quality"):
                current = str(key)
                if previous is not None and previous >= current:
                    raise ContractValidationError("array set must be lexically ordered", path=child_path)
                previous = current


def _validate_definition_fields(fields: Mapping[str, object], phase: int, *, path: str = "") -> None:
    """Validate one plain entry phase without constructing any public model."""
    from ..contracts._identity_validation import _revision
    from .models import DiscontinuityPolicy, InterpolationPolicy, Sensitivity

    _fields(fields, _DEFINITION_REQUIRED, ("numeric", "enumeration"), path=path)
    for name in _DEFINITION_ORDER:
        if name not in fields and name in ("numeric", "enumeration"):
            if phase == 2:
                _definition_cross_field(fields, name, path=path)
            continue
        value = _required(fields, name, path=path)
        child_path = f"{path}/{name}"
        if _null(value, phase, path=child_path):
            continue
        if name in ("definition_id", "quantity_id", "title", "description"):
            _text_field(value, phase, path=child_path, maximum={"title": 256, "description": 4096}.get(name))
        elif name == "definition_revision":
            _scalar_check(value, "integer", min(phase, 1), path=child_path)
            if phase == 2:
                _revision(value, path=child_path)
        elif name in ("provenance", "limitations", "allowed_validity", "allowed_quality", "applicability"):
            _definition_collection(value, name, phase, path=child_path)
        elif name in ("interpolation_policy", "discontinuity_policy", "sensitivity"):
            _tag(
                value,
                {"interpolation_policy": InterpolationPolicy, "discontinuity_policy": DiscontinuityPolicy, "sensitivity": Sensitivity}[name],
                path=child_path,
            )
        else:
            nested = cast(Mapping[str, object], value)
            if phase == 2 and name in ("numeric", "enumeration"):
                _definition_cross_field(fields, name, path=path)
            if phase == 2 and name == "coordinates":
                _coordinate_header(nested, phase, path=child_path)
                _definition_cross_field(fields, name, path=path)
            if name == "unit":
                if phase == 2:
                    _definition_cross_field(fields, name, path=path)
                _validate_unit_fields(nested, phase, path=child_path, definition=fields)
            elif name == "numeric":
                _definition_numeric_fields(fields, nested, phase, path=child_path)
            else:
                validators = {
                    "authority": _validate_authority_fields,
                    "representation": _validate_representation_fields,
                    "coordinates": _validate_coordinates_fields,
                    "enumeration": _validate_enumeration_fields,
                    "freshness": _validate_freshness_fields,
                }
                validators[name](nested, phase, path=child_path)
        if phase == 2 and name == "interpolation_policy":
            _definition_cross_field(fields, name, path=path)


def _definition_numeric_fields(fields: Mapping[str, object], numeric: Mapping[str, object], phase: int, *, path: str) -> None:
    _fields(numeric, ("storage_precision_bits", "resolution"), ("minimum", "maximum"), path=path)
    _scalar_check(_required(numeric, "storage_precision_bits", path=path), "integer", min(phase, 1), path=f"{path}/storage_precision_bits")
    representation = fields.get("representation")
    kind = representation.get("kind") if isinstance(representation, Mapping) else None
    scalar = representation.get("element_representation") if isinstance(representation, Mapping) and kind in ("fixed_array", "variable_array") else kind
    if scalar not in ("integer", "real", "vector") or phase == 2:
        _validate_numeric_fields(numeric, phase, path=path)
        return
    for name in ("resolution", "minimum", "maximum"):
        if name == "resolution" or name in numeric:
            _scalar_check(_required(numeric, name, path=path), "integer" if scalar == "integer" else "real", phase, path=f"{path}/{name}")


def _definition_cross_field(fields: Mapping[str, object], name: str, *, path: str) -> None:
    representation = cast(Mapping[str, object], fields["representation"])
    kind = representation["kind"]
    scalar = representation.get("element_representation") if kind in ("fixed_array", "variable_array") else kind
    numeric = scalar in ("integer", "real", "vector")
    child_path = f"{path}/{name}"
    if name == "unit":
        unit = cast(Mapping[str, object], fields["unit"])
        if not numeric and unit["kind"] != "unitless":
            raise ContractValidationError("representation requires unitless", path=child_path)
    elif name == "coordinates":
        coordinates = cast(Mapping[str, object], fields["coordinates"])
        if coordinates["kind"] == "applicable":
            count = len(cast(tuple[object, ...], coordinates["axes"]))
            if (kind == "vector" and count != representation["length"]) or (kind != "vector" and count > 1):
                raise ContractValidationError("coordinate axis count differs from representation", path=f"{child_path}/axes")
    elif name in ("numeric", "enumeration"):
        needed = numeric if name == "numeric" else scalar == "enumeration"
        if (name in fields) != needed:
            raise ContractValidationError("missing or irrelevant representation metadata", path=child_path)
    elif (
        name == "interpolation_policy"
        and fields[name] == "linear"
        and not (kind in ("real", "vector") or (kind in ("fixed_array", "variable_array") and numeric))
    ):
        raise ContractValidationError("linear interpolation is incompatible", path=child_path)
