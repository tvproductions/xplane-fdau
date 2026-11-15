"""Pure compatibility checks over two explicit immutable catalogs."""

from __future__ import annotations

from collections.abc import Mapping
from typing import NoReturn

from ..contracts.errors import ContractShapeError, ContractValidationError
from ..contracts.values import _OMITTED, _representation_spec_wire, _unit_spec_wire
from ..measurements.models import MeasurementCatalog, MeasurementDefinition
from ._catalog_validation import _FAMILY
from ._model_io import _source_spec_wire, _transform_step_wire
from ._source_validation import _FAILURE_ORDER
from .models import SourceBindingCatalog, SourceBindingDefinition

__all__ = ["validate_binding_catalog"]


def _fail(binding: SourceBindingDefinition, path: str, message: str) -> NoReturn:
    raise ContractValidationError(message, path=path, contract_family=_FAMILY, identity=binding.definition_id[:160])


def _measurement_metadata(measurement: MeasurementDefinition) -> tuple[object, ...]:
    rep = _representation_spec_wire(measurement.representation)
    kind = rep["kind"]
    shape: dict[str, object] = {"kind": "scalar"}
    if kind in ("vector", "fixed_array"):
        shape = {"kind": "fixed", "length": rep["length"]}
    elif kind == "variable_array":
        shape = {"kind": "variable", "minimum_length": rep["minimum_length"], "maximum_length": rep["maximum_length"]}
    return kind, rep.get("element_representation", _OMITTED), rep.get("payload", _OMITTED), shape, _unit_spec_wire(measurement.unit)


def _match_metadata(
    binding: SourceBindingDefinition, measurement: MeasurementDefinition, fields: Mapping[str, object], names: tuple[str, ...], path: str
) -> None:
    for name, expected in zip(names, _measurement_metadata(measurement), strict=True):
        if fields.get(name, _OMITTED) != expected:
            _fail(binding, path + "/" + name, "declaration must exactly match the resolved measurement")


def _applicability(binding: SourceBindingDefinition, measurement: MeasurementDefinition, path: str) -> None:
    selectors = {selector.class_id: (index, selector.value) for index, selector in enumerate(binding.applicability)}
    for selector in measurement.applicability:
        if selector.class_id not in selectors:
            _fail(binding, path, "binding must preserve every measurement applicability class")
        index, value = selectors[selector.class_id]
        if value != selector.value:
            _fail(binding, path + f"/{index}/value", "binding applicability conflicts with measurement")


def _failure_authorization(binding: SourceBindingDefinition, measurement: MeasurementDefinition, path: str) -> None:
    rows = {
        "unavailable": {"invalid", "unknown"},
        "orphaned": {"invalid", "unknown"},
        "stale": {"invalid", "unknown"},
        "read_error": {"invalid", "unknown"},
        "type_mismatch": {"invalid", "unknown"},
        "provider_degraded": {"valid", "invalid", "unknown"},
    }
    validity = set(measurement.allowed_validity)
    for condition in _FAILURE_ORDER:
        disposition = getattr(binding.failure_policy, condition)
        if disposition == "reject":
            continue
        if condition not in measurement.allowed_quality or not validity.intersection(rows[condition]):
            _fail(binding, path + "/" + condition, "failure disposition lacks measurement quality/validity authorization")
        if disposition in ("accept_raw_only", "accept_without_value") and not validity.intersection({"invalid", "unknown"}):
            _fail(binding, path + "/" + condition, "absent normalization requires invalid or unknown validity")


def validate_binding_catalog(binding_catalog: SourceBindingCatalog, measurement_catalog: MeasurementCatalog) -> None:
    """Resolve exact references and validate declarations without executing algorithms."""
    if type(binding_catalog) is not SourceBindingCatalog:
        raise ContractShapeError("expected owned source binding catalog", path="", contract_family=_FAMILY)
    if type(measurement_catalog) is not MeasurementCatalog:
        raise ContractShapeError("expected owned measurement catalog", path="", contract_family=_FAMILY)
    index = {(m.definition_id, m.definition_revision): m for m in measurement_catalog.definitions}
    for ordinal, binding in enumerate(binding_catalog.definitions):
        path = f"/definitions/{ordinal}"
        ref = binding.measurement_ref
        measurement = index.get((ref.definition_id, ref.definition_revision))
        if measurement is None:
            _fail(binding, path + "/measurement_ref", "measurement identity and revision must resolve")
        if ref.definition_hash != measurement.content_hash:
            _fail(binding, path + "/measurement_ref/definition_hash", "measurement reference hash differs from resolved definition")
        if not binding.transforms:
            _match_metadata(
                binding,
                measurement,
                _source_spec_wire(binding.source),
                ("declared_representation", "declared_element_representation", "declared_payload", "declared_shape", "native_unit"),
                path + "/source",
            )
        _applicability(binding, measurement, path + "/applicability")
        if binding.transforms:
            _match_metadata(
                binding,
                measurement,
                _transform_step_wire(binding.transforms[-1]),
                ("output_representation", "output_element_representation", "output_payload", "output_shape", "output_unit"),
                path + f"/transforms/{len(binding.transforms) - 1}",
            )
        _failure_authorization(binding, measurement, path + "/failure_policy")
