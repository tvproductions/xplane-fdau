"""Closed measurement validity and acquisition-quality vocabularies."""

from enum import StrEnum

__all__ = ["ValidityState", "QualityFlag"]  # noqa: RUF022 -- specification ownership order


class ValidityState(StrEnum):
    """Producer assertion about evidence validity for its declared use."""

    VALID = "valid"
    INVALID = "invalid"
    UNKNOWN = "unknown"
    NOT_APPLICABLE = "not_applicable"


class QualityFlag(StrEnum):
    """Acquisition evidence conditions, independent of operational findings."""

    CONVERSION_FAILED = "conversion_failed"
    DISCONTINUOUS = "discontinuous"
    DROPPED = "dropped"
    DUPLICATE = "duplicate"
    ORPHANED = "orphaned"
    OUT_OF_DECLARED_RANGE = "out_of_declared_range"
    PRECISION_LOST = "precision_lost"
    PROVIDER_DEGRADED = "provider_degraded"
    READ_ERROR = "read_error"
    REORDERED = "reordered"
    ROUNDED = "rounded"
    SATURATED = "saturated"
    STALE = "stale"
    TYPE_MISMATCH = "type_mismatch"
    UNAVAILABLE = "unavailable"
