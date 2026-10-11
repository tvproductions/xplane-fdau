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
from .provenance import AdapterIdentity, Authority, ProducerIdentity, ProvenanceSource, ProviderIdentity
from .values import (
    ValueRepresentation,
    ScalarRepresentation,
    RetentionStatus,
    InlineValue,
    PayloadReference,
    PayloadSpec,
    RepresentationSpec,
    ShapeSpec,
    UnitSpec,
)

__all__ = [
    "FDAUContractError",
    "ContractParseError",
    "ContractShapeError",
    "ContractValidationError",
    "CanonicalJSONError",
    "UnsupportedContractVersionError",
    "ContractHashError",
    "DefinitionRef",
    "RecordRef",
    "AlgorithmRef",
    "Authority",
    "ProvenanceSource",
    "ProducerIdentity",
    "ProviderIdentity",
    "AdapterIdentity",
    "ValueRepresentation",
    "ScalarRepresentation",
    "RetentionStatus",
    "InlineValue",
    "PayloadReference",
    "PayloadSpec",
    "RepresentationSpec",
    "ShapeSpec",
    "UnitSpec",
    "canonical_bytes",
]
