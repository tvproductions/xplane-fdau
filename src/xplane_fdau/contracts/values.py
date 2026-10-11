"""Immutable typed values for canonical FDAU contracts."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
import math
import re

from ._identity_validation import _counter, _identifier, _integer_domain, _nfc_text, _sha256, _text
from .errors import CanonicalJSONError, ContractShapeError, ContractValidationError

__all__ = [
    "ValueRepresentation",
    "ScalarRepresentation",
    "RetentionStatus",
    "InlineValue",
    "PayloadReference",
    "PayloadSpec",
    "RepresentationSpec",
    "ShapeSpec",
    "UnitSpec",
]


class ValueRepresentation(StrEnum):
    """Closed set of inline and referenced-byte representations."""

    BOOLEAN = "boolean"
    INTEGER = "integer"
    REAL = "real"
    STRING = "string"
    ENUMERATION = "enumeration"
    VECTOR = "vector"
    FIXED_ARRAY = "fixed_array"
    VARIABLE_ARRAY = "variable_array"
    REFERENCED_BYTES = "referenced_bytes"


class ScalarRepresentation(StrEnum):
    """Primitive representations permitted as array elements."""

    BOOLEAN = "boolean"
    INTEGER = "integer"
    REAL = "real"
    STRING = "string"
    ENUMERATION = "enumeration"


_OMITTED = object()


def _tag(value: object, vocabulary: type[StrEnum], *, path: str) -> StrEnum:
    if type(value) not in (str, vocabulary):
        raise ContractShapeError("expected representation tag", path=path)
    try:
        return vocabulary(value)
    except ValueError:
        raise ContractShapeError("unknown representation tag", path=path) from None


def _scalar_check(value: object, representation: str, phase: int, *, path: str) -> None:
    if value is None:
        if phase == 0:
            return
        raise CanonicalJSONError("null is prohibited", path=path)
    expected = {"boolean": bool, "integer": int, "real": float, "string": str, "enumeration": str}[representation]
    if phase == 0:
        if type(value) is not expected:
            raise ContractShapeError("unexpected primitive type", path=path)
    elif phase == 1:
        if representation == "integer":
            _integer_domain(value, path=path)
        elif representation == "real":
            if not isinstance(value, float) or not math.isfinite(value):
                raise CanonicalJSONError("nonfinite binary64", path=path)
        elif representation in ("string", "enumeration"):
            _text(value, path=path)
    elif representation == "string":
        _nfc_text(value, path=path, maximum=16384)
    elif representation == "enumeration":
        _identifier(value, path=path)


def _inline_check(representation: object, element: object, value: object, phase: int) -> tuple[ValueRepresentation, object, object]:
    tag = ValueRepresentation(_tag(representation, ValueRepresentation, path="/representation"))
    if tag == ValueRepresentation.REFERENCED_BYTES:
        raise ContractShapeError("bytes require a payload reference", path="/representation")
    array = tag in (ValueRepresentation.FIXED_ARRAY, ValueRepresentation.VARIABLE_ARRAY)
    if array:
        element = ScalarRepresentation(_tag(element, ScalarRepresentation, path="/element_representation"))
    elif element is not _OMITTED:
        raise ContractShapeError("irrelevant element representation", path="/element_representation")
    if value is None:
        if phase == 0:
            return tag, element, value
        raise CanonicalJSONError("null is prohibited", path="/value")
    if array or tag == ValueRepresentation.VECTOR:
        if type(value) not in (list, tuple):
            raise ContractShapeError("expected ordered array", path="/value")
        assert isinstance(value, (list, tuple))
        scalar = str(element) if array else "real"
        for index, item in enumerate(value):
            _scalar_check(item, scalar, phase, path=f"/value/{index}")
        if phase == 2 and (len(value) > 65535 or tag == ValueRepresentation.VECTOR and not value):
            raise ContractValidationError("value count outside range", path="/value")
        value = tuple(value)
    else:
        _scalar_check(value, tag, phase, path="/value")
    return tag, element, value


@dataclass(frozen=True, slots=True, kw_only=True)
class InlineValue:
    """Preserve the primitive type and ordered contents of an inline value."""

    representation: ValueRepresentation | str
    element_representation: object = _OMITTED
    value: object

    def __post_init__(self) -> None:
        tag, element, value = self.representation, self.element_representation, self.value
        for phase in range(3):
            tag, element, value = _inline_check(tag, element, value, phase)
        object.__setattr__(self, "representation", tag)
        object.__setattr__(self, "element_representation", element)
        object.__setattr__(self, "value", value)


def _inline_value_wire(value: InlineValue) -> dict[str, object]:
    result: dict[str, object] = {"representation": str(value.representation)}
    if value.element_representation is not _OMITTED:
        result["element_representation"] = str(value.element_representation)
    result["value"] = list(value.value) if isinstance(value.value, tuple) else value.value
    return result


class RetentionStatus(StrEnum):
    """Disposition of the original claimed byte sequence."""

    RETAINED = "retained"
    INTENTIONALLY_OMITTED = "intentionally_omitted"
    MISSING = "missing"
    UNVERIFIED = "unverified"


@dataclass(frozen=True, slots=True, kw_only=True)
class PayloadReference:
    """Describe content-addressed bytes without resolving their storage."""

    media_type: str
    byte_length: int
    sha256: str
    storage_role: str
    retention_status: RetentionStatus | str

    def __post_init__(self) -> None:
        for path, value, domain in (
            ("/media_type", self.media_type, "string"),
            ("/byte_length", self.byte_length, "integer"),
            ("/sha256", self.sha256, "string"),
            ("/storage_role", self.storage_role, "string"),
        ):
            _scalar_check(value, domain, 0, path=path)
        status = _tag(self.retention_status, RetentionStatus, path="/retention_status")
        _basic_domains(
            ("/media_type", self.media_type, "text"),
            ("/byte_length", self.byte_length, "integer"),
            ("/sha256", self.sha256, "text"),
            ("/storage_role", self.storage_role, "text"),
        )
        _media_type(self.media_type, path="/media_type")
        _counter(self.byte_length, path="/byte_length")
        _sha256(self.sha256, path="/sha256")
        _identifier(self.storage_role, path="/storage_role")
        object.__setattr__(self, "retention_status", status)


_MEDIA_TYPE = re.compile(r"[a-z0-9][a-z0-9!#$&^_.+-]{0,126}/[a-z0-9][a-z0-9!#$&^_.+-]{0,126}\Z")


def _media_type(value: object, *, path: str) -> str:
    checked = _nfc_text(value, path=path, maximum=127)
    if _MEDIA_TYPE.fullmatch(checked) is None:
        raise ContractValidationError("invalid media type", path=path)
    return checked


def _payload_reference_wire(value: PayloadReference) -> dict[str, object]:
    return {
        "media_type": value.media_type,
        "byte_length": value.byte_length,
        "sha256": value.sha256,
        "storage_role": value.storage_role,
        "retention_status": str(value.retention_status),
    }


@dataclass(frozen=True, slots=True, kw_only=True)
class PayloadSpec:
    """Declare the ordered media types and roles authorized for payloads."""

    allowed_media_types: object
    allowed_storage_roles: object

    def __post_init__(self) -> None:
        fields = (("/allowed_media_types", self.allowed_media_types), ("/allowed_storage_roles", self.allowed_storage_roles))
        for phase in range(3):
            for path, value in fields:
                _array_set_check(value, phase, path=path, media=path == "/allowed_media_types")
        for path, value in fields:
            assert isinstance(value, (list, tuple))
            object.__setattr__(self, path[1:], tuple(value))


@dataclass(frozen=True, slots=True, kw_only=True)
class RepresentationSpec:
    """Declare one representation and its variant-specific constraints."""

    kind: ValueRepresentation | str
    element_representation: object = _OMITTED
    length: object = _OMITTED
    minimum_length: object = _OMITTED
    maximum_length: object = _OMITTED
    payload: object = _OMITTED

    def __post_init__(self) -> None:
        kind = ValueRepresentation(_tag(self.kind, ValueRepresentation, path="/kind"))
        fields = {
            "element_representation": self.element_representation,
            "length": self.length,
            "minimum_length": self.minimum_length,
            "maximum_length": self.maximum_length,
            "payload": self.payload,
        }
        selected: tuple[str, ...] = ()
        if kind == ValueRepresentation.VECTOR:
            selected = ("length",)
        elif kind == ValueRepresentation.FIXED_ARRAY:
            selected = ("element_representation", "length")
        elif kind == ValueRepresentation.VARIABLE_ARRAY:
            selected = ("element_representation", "minimum_length", "maximum_length")
        elif kind == ValueRepresentation.REFERENCED_BYTES:
            selected = ("payload",)
        _variant_fields(fields, selected)
        if "element_representation" in selected:
            element = ScalarRepresentation(_tag(self.element_representation, ScalarRepresentation, path="/element_representation"))
            object.__setattr__(self, "element_representation", element)
        if "payload" in selected and self.payload is None:
            raise CanonicalJSONError("null is prohibited", path="/payload")
        _length_fields(fields, selected, maximum=1024 if kind == ValueRepresentation.VECTOR else 65535)
        object.__setattr__(self, "kind", kind)


@dataclass(frozen=True, slots=True, kw_only=True)
class ShapeSpec:
    """Declare scalar, fixed, or variable one-dimensional shape."""

    kind: str
    length: object = _OMITTED
    minimum_length: object = _OMITTED
    maximum_length: object = _OMITTED

    def __post_init__(self) -> None:
        kind = _choice(self.kind, ("scalar", "fixed", "variable"), path="/kind")
        fields = {"length": self.length, "minimum_length": self.minimum_length, "maximum_length": self.maximum_length}
        selected = () if kind == "scalar" else ("length",) if kind == "fixed" else ("minimum_length", "maximum_length")
        _variant_fields(fields, selected)
        _length_fields(fields, selected, maximum=65535)


@dataclass(frozen=True, slots=True, kw_only=True)
class UnitSpec:
    """Declare qualified quantity/unit identities or explicit unitless status."""

    kind: str
    quantity_id: object = _OMITTED
    unit_id: object = _OMITTED

    def __post_init__(self) -> None:
        kind = _choice(self.kind, ("unitless", "unit"), path="/kind")
        fields = {"quantity_id": self.quantity_id, "unit_id": self.unit_id}
        selected = () if kind == "unitless" else ("quantity_id", "unit_id")
        _variant_fields(fields, selected)
        _basic_domains(*(("/" + name, fields[name], "text") for name in selected))
        for name in selected:
            _identifier(fields[name], path="/" + name)


def _choice(value: object, choices: tuple[str, ...], *, path: str) -> str:
    if type(value) is not str or value not in choices:
        raise ContractShapeError("unknown variant", path=path)
    return value


def _variant_fields(fields: dict[str, object], selected: tuple[str, ...]) -> None:
    for name, value in fields.items():
        if (name in selected) == (value is _OMITTED):
            raise ContractShapeError("missing or irrelevant variant property", path="/" + name)
        if name not in selected or value is None:
            continue
        if name == "element_representation":
            _tag(value, ScalarRepresentation, path="/" + name)
        elif name == "payload":
            if type(value) is not PayloadSpec:
                raise ContractShapeError("expected payload declaration", path="/payload")
        else:
            _scalar_check(value, "string" if name in ("quantity_id", "unit_id") else "integer", 0, path="/" + name)


def _length_fields(fields: dict[str, object], selected: tuple[str, ...], *, maximum: int) -> None:
    names = tuple(name for name in selected if name in ("length", "minimum_length", "maximum_length"))
    _basic_domains(*(("/" + name, fields[name], "integer") for name in names))
    for name in names:
        value = _counter(fields[name], path="/" + name)
        if not (1 if name == "length" else 0) <= value <= maximum:
            raise ContractValidationError("declared length outside range", path="/" + name)
    if "minimum_length" in names:
        minimum = fields["minimum_length"]
        maximum_value = fields["maximum_length"]
        assert isinstance(minimum, int) and isinstance(maximum_value, int)
        if minimum > maximum_value:
            raise ContractValidationError("minimum exceeds maximum length", path="/minimum_length")


def _array_set_check(value: object, phase: int, *, path: str, media: bool) -> None:
    if value is None:
        if phase == 0:
            return
        raise CanonicalJSONError("null is prohibited", path=path)
    if type(value) not in (list, tuple):
        raise ContractShapeError("expected ordered array", path=path)
    assert isinstance(value, (list, tuple))
    for index, item in enumerate(value):
        _scalar_check(item, "string", min(phase, 1), path=f"{path}/{index}")
    if phase == 2:
        if not 1 <= len(value) <= 65535:
            raise ContractValidationError("allow-list count outside range", path=path)
        previous: str | None = None
        for index, item in enumerate(value):
            item_path = f"{path}/{index}"
            checked = _media_type(item, path=item_path) if media else _identifier(item, path=item_path)
            if previous is not None and previous >= checked:
                raise ContractValidationError("allow-list is duplicate or unordered", path=item_path)
            previous = checked


def _basic_domains(*fields: tuple[str, object, str]) -> None:
    for phase in range(2):
        for path, value, kind in fields:
            _scalar_check(value, "string" if kind == "text" else "integer", phase, path=path)


def _payload_spec_wire(value: PayloadSpec) -> dict[str, object]:
    assert isinstance(value.allowed_media_types, tuple) and isinstance(value.allowed_storage_roles, tuple)
    return {"allowed_media_types": list(value.allowed_media_types), "allowed_storage_roles": list(value.allowed_storage_roles)}


def _representation_spec_wire(value: RepresentationSpec) -> dict[str, object]:
    result: dict[str, object] = {"kind": str(value.kind)}
    for name, field in (
        ("element_representation", value.element_representation),
        ("length", value.length),
        ("minimum_length", value.minimum_length),
        ("maximum_length", value.maximum_length),
    ):
        if field is not _OMITTED:
            result[name] = str(field) if name == "element_representation" else field
    if type(value.payload) is PayloadSpec:
        result["payload"] = _payload_spec_wire(value.payload)
    return result


def _shape_spec_wire(value: ShapeSpec) -> dict[str, object]:
    result: dict[str, object] = {"kind": value.kind}
    for name, field in (("length", value.length), ("minimum_length", value.minimum_length), ("maximum_length", value.maximum_length)):
        if field is not _OMITTED:
            result[name] = field
    return result


def _unit_spec_wire(value: UnitSpec) -> dict[str, object]:
    result: dict[str, object] = {"kind": value.kind}
    if value.kind == "unit":
        result.update(quantity_id=value.quantity_id, unit_id=value.unit_id)
    return result
