"""Private strict inputs for measurement validity and quality array sets."""

from __future__ import annotations

from typing import cast

from ..contracts.errors import CanonicalJSONError, ContractShapeError, ContractValidationError
from .models import QualityFlag, ValidityState


def _validity_state(value: object, *, path: str = "/validity") -> ValidityState:
    """Retain one explicit producer assertion without inferring a state."""
    if value is None:
        raise CanonicalJSONError("null is prohibited", path=path)
    if type(value) not in (str, ValidityState):
        raise ContractShapeError("expected validity vocabulary", path=path)
    try:
        return ValidityState(value)
    except ValueError:
        raise ContractShapeError("unknown validity vocabulary", path=path) from None


def _quality_flags(value: object, *, path: str = "/quality") -> tuple[QualityFlag, ...]:
    """Copy an already ordered array set, rejecting coercion and reordering."""
    if value is None:
        raise CanonicalJSONError("null is prohibited", path=path)
    if type(value) not in (list, tuple):
        raise ContractShapeError("expected quality array", path=path)
    items = cast(list[object] | tuple[object, ...], value)
    for index, item in enumerate(items):
        if item is not None and (type(item) not in (str, QualityFlag) or item not in QualityFlag):
            raise ContractShapeError("unknown quality vocabulary", path=f"{path}/{index}")
    for index, item in enumerate(items):
        if item is None:
            raise CanonicalJSONError("null is prohibited", path=f"{path}/{index}")
    flags = tuple(QualityFlag(item) for item in items)
    for index in range(1, len(flags)):
        if flags[index - 1].value >= flags[index].value:
            raise ContractValidationError("quality flags must be unique and lexically ordered", path=f"{path}/{index}")
    return flags
