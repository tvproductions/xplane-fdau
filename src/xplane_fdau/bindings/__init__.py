"""Source-binding declarations for transport-free X-Plane evidence."""

from .io import dump_source_binding_catalog_v1, dumps_source_binding_catalog_v1, load_source_binding_catalog_v1, loads_source_binding_catalog_v1
from .models import (
    AcquisitionPhase,
    BindingInputRef,
    BindingReplayPolicy,
    CompanionRole,
    CompanionSource,
    FailureCondition,
    FailureDisposition,
    FailurePolicy,
    SourceBindingCatalog,
    SourceBindingDefinition,
    SourceSpec,
    TransformInput,
    TransformStep,
)
from .validation import validate_binding_catalog

__all__ = [  # noqa: RUF022 -- specification ownership order
    "CompanionRole",
    "FailureCondition",
    "FailureDisposition",
    "AcquisitionPhase",
    "BindingReplayPolicy",
    "BindingInputRef",
    "CompanionSource",
    "TransformInput",
    "TransformStep",
    "FailurePolicy",
    "SourceSpec",
    "SourceBindingDefinition",
    "SourceBindingCatalog",
    "load_source_binding_catalog_v1",
    "loads_source_binding_catalog_v1",
    "dump_source_binding_catalog_v1",
    "dumps_source_binding_catalog_v1",
    "validate_binding_catalog",
]
