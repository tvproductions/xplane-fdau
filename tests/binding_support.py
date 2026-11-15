"""Synthetic fixtures for source-binding contract tests."""

from __future__ import annotations

import importlib
from typing import Any

from xplane_fdau.contracts.identity import AlgorithmRef
from xplane_fdau.contracts.provenance import AdapterIdentity, ProviderIdentity
from xplane_fdau.contracts.values import PayloadSpec, ShapeSpec, UnitSpec


def model(name: str) -> Any:
    return getattr(importlib.import_module("xplane_fdau.bindings.models"), name)


def unit() -> UnitSpec:
    return UnitSpec(kind="unit", quantity_id="test.length", unit_id="test.feet")


def payload() -> PayloadSpec:
    return PayloadSpec(allowed_media_types=["application/octet-stream"], allowed_storage_roles=["test.raw"])


def source(**changes: Any) -> Any:
    fields = dict(
        provider=ProviderIdentity(provider_family_id="test.provider", provider_version="1"),
        adapter=AdapterIdentity(adapter_family_id="test.adapter", adapter_version="1"),
        resource_kind="test.resource",
        resource_id="test.primary",
        declared_representation="real",
        declared_shape=ShapeSpec(kind="scalar"),
        native_unit=unit(),
    )
    fields.update(changes)
    return model("SourceSpec")(**fields)


def algorithm(**changes: Any) -> AlgorithmRef:
    fields: dict[str, Any] = dict(definition_id="test.convert", definition_revision=1, definition_hash="a" * 64, parameters={})
    fields.update(changes)
    return AlgorithmRef(**fields)


def transform_input(**changes: Any) -> Any:
    fields = dict(input_id="binding.primary", representation="real", shape=ShapeSpec(kind="scalar"), unit=unit())
    fields.update(changes)
    return model("TransformInput")(**fields)


def transform(**changes: Any) -> Any:
    fields = dict(
        step_id="test.convert",
        algorithm=algorithm(),
        inputs=[transform_input()],
        output_representation="real",
        output_shape=ShapeSpec(kind="scalar"),
        output_unit=unit(),
    )
    fields.update(changes)
    return model("TransformStep")(**fields)


def failure(**changes: Any) -> Any:
    fields = dict.fromkeys(("unavailable", "orphaned", "stale", "read_error", "type_mismatch", "provider_degraded"), "reject")
    fields.update(changes)
    return model("FailurePolicy")(**fields)
