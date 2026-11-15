"""Plain-field phases for inert transform declarations."""

from __future__ import annotations

from collections.abc import Mapping
from typing import cast

from ..contracts.errors import ContractValidationError
from ..contracts.values import _ordered_array
from ..measurements._definition_validation import _fields, _null, _required, _text_field
from ._source_validation import _validate_ref_fields, _validate_value_fields

_INPUT_NAMES = ("representation", "element_representation", "payload", "shape", "unit")
_OUTPUT_NAMES = ("output_representation", "output_element_representation", "output_payload", "output_shape", "output_unit")


def _validate_transform_input_fields(fields: Mapping[str, object], phase: int, *, path: str = "") -> None:
    _fields(fields, ("input_id", "representation", "shape", "unit"), ("element_representation", "payload"), path=path)
    _text_field(_required(fields, "input_id", path=path), phase, path=path + "/input_id")
    _validate_value_fields(fields, phase, _INPUT_NAMES, path=path)


def _validate_transform_step_fields(fields: Mapping[str, object], phase: int, *, path: str = "") -> None:
    _fields(
        fields,
        ("step_id", "algorithm", "inputs", "output_representation", "output_shape", "output_unit"),
        ("output_element_representation", "output_payload"),
        path=path,
    )
    _text_field(_required(fields, "step_id", path=path), phase, path=path + "/step_id")
    _validate_ref_fields(_required(fields, "algorithm", path=path), phase, path=path + "/algorithm", algorithm=True)
    value = _required(fields, "inputs", path=path)
    if not _null(value, phase, path=path + "/inputs"):
        inputs = _ordered_array(value, path=path + "/inputs")
        if phase == 2 and not inputs:
            raise ContractValidationError("transform inputs must be nonempty", path=path + "/inputs")
        for index, item in enumerate(inputs):
            child_path = path + f"/inputs/{index}"
            if not _null(item, phase, path=child_path):
                _validate_transform_input_fields(cast(Mapping[str, object], item), phase, path=child_path)
    _validate_value_fields(fields, phase, _OUTPUT_NAMES, path=path)
