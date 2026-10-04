"""Shared FDAU contract primitives."""

from .canonical_json import canonical_bytes

from .errors import (
    CanonicalJSONError,
    ContractHashError,
    ContractParseError,
    ContractShapeError,
    ContractValidationError,
    FDAUContractError,
    UnsupportedContractVersionError,
)
from .identity import AlgorithmRef, DefinitionRef, RecordRef

__all__ = [
    "FDAUContractError",
    "ContractParseError",
    "ContractShapeError",
    "ContractValidationError",
    "CanonicalJSONError",
    "UnsupportedContractVersionError",
    "ContractHashError",
    "canonical_bytes",
    "DefinitionRef",
    "RecordRef",
    "AlgorithmRef",
]
