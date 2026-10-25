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
    InlineValue,
    PayloadReference,
    PayloadSpec,
    RepresentationSpec,
    RetentionStatus,
    ScalarRepresentation,
    ShapeSpec,
    UnitSpec,
    ValueRepresentation,
)

__all__ = [
    "AdapterIdentity",
    "AlgorithmRef",
    "Authority",
    "CanonicalJSONError",
    "ContractHashError",
    "ContractParseError",
    "ContractShapeError",
    "ContractValidationError",
    "DefinitionRef",
    "FDAUContractError",
    "InlineValue",
    "PayloadReference",
    "PayloadSpec",
    "ProducerIdentity",
    "ProvenanceSource",
    "ProviderIdentity",
    "RecordRef",
    "RepresentationSpec",
    "RetentionStatus",
    "ScalarRepresentation",
    "ShapeSpec",
    "UnitSpec",
    "UnsupportedContractVersionError",
    "ValueRepresentation",
    "canonical_bytes",
]
