"""Plain-field phases and local graph checks for inert transforms."""

from __future__ import annotations

from collections.abc import Mapping
from typing import cast

from ..contracts.errors import ContractValidationError
from ..contracts.values import _ordered_array
from ..measurements._definition_validation import _fields, _null, _required, _text_field
from ._source_validation import _validate_ref_fields, _validate_value_fields

_INPUT_NAMES = ("representation", "element_representation", "payload", "shape", "unit")
_OUTPUT_NAMES = ("output_representation", "output_element_representation", "output_payload", "output_shape", "output_unit")


def _source_value_metadata(fields: Mapping[str, object]) -> dict[str, object]:
    """Project the source's declared value metadata, with optional presence exact."""
    names = ("declared_representation", "declared_element_representation", "declared_payload", "declared_shape", "native_unit")
    return {target: fields[name] for name, target in zip(names, _INPUT_NAMES, strict=True) if name in fields}


def _validate_input(
    fields: Mapping[str, object],
    phase: int,
    *,
    path: str,
    symbols: Mapping[str, Mapping[str, object]] | None = None,
) -> None:
    _fields(fields, ("input_id", "representation", "shape", "unit"), ("element_representation", "payload"), path=path)
    identity = _required(fields, "input_id", path=path)
    _text_field(identity, phase, path=path + "/input_id")
    expected = None
    if phase == 2 and symbols is not None:
        if identity not in symbols:
            raise ContractValidationError("input must resolve to a primary, dependency or preceding step", path=path + "/input_id")
        expected = symbols[cast(str, identity)]
    _validate_value_fields(fields, phase, _INPUT_NAMES, path=path, expected=expected)


def _validate_transform_input_fields(fields: Mapping[str, object], phase: int, *, path: str = "") -> None:
    _validate_input(fields, phase, path=path)


def _validate_step(
    fields: Mapping[str, object],
    phase: int,
    *,
    path: str,
    symbols: dict[str, Mapping[str, object]] | None = None,
    reserved: set[str] | None = None,
) -> None:
    _fields(
        fields,
        ("step_id", "algorithm", "inputs", "output_representation", "output_shape", "output_unit"),
        ("output_element_representation", "output_payload"),
        path=path,
    )
    identity = _required(fields, "step_id", path=path)
    _text_field(identity, phase, path=path + "/step_id")
    if phase == 2 and symbols is not None and (identity in symbols or (reserved is not None and identity in reserved)):
        raise ContractValidationError("step identity is duplicate or reserved", path=path + "/step_id")
    _validate_ref_fields(_required(fields, "algorithm", path=path), phase, path=path + "/algorithm", algorithm=True)
    value = _required(fields, "inputs", path=path)
    if not _null(value, phase, path=path + "/inputs"):
        inputs = _ordered_array(value, path=path + "/inputs")
        if phase == 2 and not inputs:
            raise ContractValidationError("transform inputs must be nonempty", path=path + "/inputs")
        for index, item in enumerate(inputs):
            child_path = path + f"/inputs/{index}"
            if not _null(item, phase, path=child_path):
                _validate_input(cast(Mapping[str, object], item), phase, path=child_path, symbols=symbols)
    _validate_value_fields(fields, phase, _OUTPUT_NAMES, path=path)
    if phase == 2 and symbols is not None:
        symbols[cast(str, identity)] = {target: fields[name] for name, target in zip(_OUTPUT_NAMES, _INPUT_NAMES, strict=True) if name in fields}


def _validate_transform_step_fields(fields: Mapping[str, object], phase: int, *, path: str = "") -> None:
    _validate_step(fields, phase, path=path)


def _validate_step_graph(fields: Mapping[str, object], symbols: dict[str, Mapping[str, object]], reserved: set[str], *, path: str) -> None:
    """Check edges at their semantic input fields, then publish the step output."""
    _validate_step(fields, 2, path=path, symbols=symbols, reserved=reserved)
