"""Source-binding declarations for transport-free X-Plane evidence."""

from .models import (
    AcquisitionPhase,
    BindingInputRef,
    BindingReplayPolicy,
    CompanionRole,
    CompanionSource,
    FailureCondition,
    FailureDisposition,
    FailurePolicy,
    SourceSpec,
    TransformInput,
    TransformStep,
)

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
]
