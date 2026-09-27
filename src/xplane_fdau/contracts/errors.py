"""Contextual errors for canonical FDAU contracts."""

from __future__ import annotations

__all__ = [
    "FDAUContractError",
    "ContractParseError",
    "ContractShapeError",
    "ContractValidationError",
    "CanonicalJSONError",
    "UnsupportedContractVersionError",
    "ContractHashError",
]


class FDAUContractError(ValueError):
    """Base error with source and JSON Pointer context."""

    def __init__(
        self,
        message: str,
        *,
        source: str = "<memory>",
        line: int | None = None,
        column: int | None = None,
        path: str = "",
        contract_family: str | None = None,
        identity: str | None = None,
    ) -> None:
        self._source = source
        self._line = line
        self._column = column
        self._path = path
        self._contract_family = contract_family
        self._identity = identity
        super().__init__(message)

    @property
    def source(self) -> str:
        return self._source

    @property
    def line(self) -> int | None:
        return self._line

    @property
    def column(self) -> int | None:
        return self._column

    @property
    def path(self) -> str:
        return self._path

    @property
    def contract_family(self) -> str | None:
        return self._contract_family

    @property
    def identity(self) -> str | None:
        return self._identity


class ContractParseError(FDAUContractError):
    """Invalid JSON syntax, encoding, or duplicate property."""


class ContractShapeError(FDAUContractError):
    """Invalid contract envelope or property shape."""


class ContractValidationError(FDAUContractError):
    """Invalid contract semantics."""


class CanonicalJSONError(FDAUContractError):
    """Value outside the canonical JSON domain."""


class UnsupportedContractVersionError(FDAUContractError):
    """Unrecognized contract family or schema version."""


class ContractHashError(FDAUContractError):
    """Declared content hash differs from the computed hash."""
