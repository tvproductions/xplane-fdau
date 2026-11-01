"""Strict family I/O, whole-document precedence and construction barriers."""

from __future__ import annotations

import io
import json
import unittest
from contextlib import ExitStack
from copy import deepcopy
from typing import Any, cast, override
from unittest import mock

from tests.measurement_catalog_support import FAMILY, GOLDEN_CATALOG, catalog, definition
from tests.test_measurement_definition_io import signed
from xplane_fdau import measurements
from xplane_fdau.contracts import (
    Authority,
    CanonicalJSONError,
    ContractHashError,
    ContractParseError,
    ContractShapeError,
    ContractValidationError,
    DefinitionRef,
    FDAUContractError,
    ProvenanceSource,
    UnsupportedContractVersionError,
)
from xplane_fdau.contracts.values import PayloadSpec, RepresentationSpec, UnitSpec
from xplane_fdau.measurements import models


def signed_catalog(fields: dict[str, Any]) -> dict[str, Any]:
    import hashlib

    result = deepcopy(fields)
    result.pop("content_hash", None)
    preimage = json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode() + b"\n"
    result["content_hash"] = hashlib.sha256(preimage).hexdigest()
    return result


def raw_pair() -> dict[str, Any]:
    fields = json.loads(GOLDEN_CATALOG)
    second = deepcopy(fields["definitions"][0])
    second["definition_id"] = "test.second"
    fields["definitions"].append(signed(second))
    return signed_catalog(fields)


class CatalogIOTests(unittest.TestCase):
    @override
    def setUp(self) -> None:
        self.assertTrue(hasattr(measurements, "loads_measurement_catalog_v1"), "public catalog I/O is missing")
        self.loads = measurements.loads_measurement_catalog_v1
        self.dumps = measurements.dumps_measurement_catalog_v1

    def assertFailure(self, raw: object, error: type[FDAUContractError], path: str) -> FDAUContractError:
        data = json.dumps(raw) if not isinstance(raw, (str, bytes)) else raw
        with self.assertRaises(error) as caught:
            self.loads(data, source="catalog.json")
        self.assertEqual(path, caught.exception.path)
        self.assertEqual("catalog.json", caught.exception.source)
        self.assertEqual(FAMILY, caught.exception.contract_family)
        return caught.exception

    def test_round_trip_text_bytes_and_member_order(self) -> None:
        self.assertEqual(GOLDEN_CATALOG, self.dumps(self.loads(GOLDEN_CATALOG)))
        raw = json.loads(GOLDEN_CATALOG)
        reordered = dict(reversed(tuple(raw.items())))
        self.assertEqual(GOLDEN_CATALOG, self.dumps(self.loads(json.dumps(reordered, indent=2))))
        self.assertEqual(catalog(), self.loads(GOLDEN_CATALOG.decode()))

    def test_exact_reference_triples_survive_round_trip(self) -> None:
        value = catalog(definitions=[definition(definition_revision=1), definition(definition_revision=2)])

        def refs(value: Any) -> tuple[DefinitionRef, ...]:
            return tuple(
                DefinitionRef(definition_id=d.definition_id, definition_revision=d.definition_revision, definition_hash=d.content_hash)
                for d in value.definitions
            )

        self.assertEqual(refs(value), refs(self.loads(self.dumps(value))))

    def test_envelope_dispatch_and_wrong_types(self) -> None:
        for name, value, error in [
            ("contract_family", "test.other", UnsupportedContractVersionError),
            ("schema_version", 2, UnsupportedContractVersionError),
            ("schema_version", True, ContractShapeError),
            ("schema_version", 1.0, ContractShapeError),
            ("contract_family", 1, ContractShapeError),
            ("schema_version", None, CanonicalJSONError),
        ]:
            raw = json.loads(GOLDEN_CATALOG)
            raw[name] = value
            if error is UnsupportedContractVersionError:
                raw["definitions"] = "bad body"
            with self.subTest(name=name, value=value):
                self.assertFailure(raw, error, "/" + name)
        for name in ("contract_family", "schema_version"):
            raw = json.loads(GOLDEN_CATALOG)
            del raw[name]
            self.assertFailure(raw, ContractShapeError, "/" + name)
        for raw in ([], 1, "true"):
            self.assertFailure(raw, ContractShapeError, "")
        self.assertFailure("null", CanonicalJSONError, "")

    def test_parse_priority_and_source_locations(self) -> None:
        for data in (b"\xef\xbb\xbf{}", b"\xff", b"{", '{"a":9223372036854775808,"a":0}'):
            error = self.assertFailure(data, ContractParseError, "/a" if isinstance(data, str) else "")
            if data == b"{":
                self.assertEqual((1, 2), (error.line, error.column))
        raw = GOLDEN_CATALOG.replace(b'"title":"Boolean"', b'"title":"Boolean","title":"Again"')
        self.assertFailure(raw, ContractParseError, "/definitions/0/title")

    def test_forbidden_properties_and_escaped_paths(self) -> None:
        for name in ("$schema", "producer", "provider", "adapter", "resource", "created_at", "bad~/field"):
            raw = json.loads(GOLDEN_CATALOG)
            raw[name] = {}
            path = "/" + name.replace("~", "~0").replace("/", "~1")
            self.assertFailure(raw, ContractShapeError, path)
        raw = json.loads(GOLDEN_CATALOG)
        raw["definitions"][0]["resource_id"] = "test.resource"
        error = self.assertFailure(raw, ContractShapeError, "/definitions/0/resource_id")
        self.assertEqual("test.boolean", error.identity)

    def test_global_shape_before_earlier_entry_hash(self) -> None:
        raw = raw_pair()
        raw["definitions"][0]["content_hash"] = "0" * 64
        del raw["definitions"][1]["title"]
        self.assertFailure(raw, ContractShapeError, "/definitions/1/title")

    def test_global_domains_before_any_hash(self) -> None:
        for field, value in (("title", "e\u0301"), ("title", "\ud800"), ("title", None), ("definition_revision", 2**63)):
            raw = raw_pair()
            raw["catalog_id"] = "bad"
            raw["definitions"][0]["content_hash"] = "0" * 64
            raw["definitions"][1][field] = value
            self.assertFailure(raw, CanonicalJSONError, "/definitions/1/" + field)

    def test_hashes_before_semantics(self) -> None:
        raw = raw_pair()
        raw["definitions"].reverse()
        raw["definitions"][0]["content_hash"] = "0" * 64
        raw["content_hash"] = "0" * 64
        self.assertFailure(raw, ContractHashError, "/definitions/0/content_hash")
        raw = raw_pair()
        raw["definitions"].reverse()
        self.assertFailure(raw, ContractHashError, "/content_hash")
        raw = signed_catalog(raw)
        self.assertFailure(raw, ContractValidationError, "/definitions/1/definition_id")
        raw["definitions"][1] = deepcopy(raw["definitions"][0])
        self.assertFailure(signed_catalog(raw), ContractValidationError, "/definitions/1/definition_revision")

    def test_malformed_root_hash_preserves_semantic_order(self) -> None:
        raw = json.loads(GOLDEN_CATALOG)
        raw.update(catalog_id="not-an-identifier", content_hash="BAD")
        self.assertFailure(raw, ContractValidationError, "/catalog_id")
        raw["catalog_id"] = "test.catalog"
        self.assertFailure(raw, ContractValidationError, "/content_hash")

    def test_well_formed_root_hash_mismatch_precedes_semantic_error(self) -> None:
        raw = json.loads(GOLDEN_CATALOG)
        raw.update(catalog_id="not-an-identifier", content_hash="0" * 64)
        self.assertFailure(raw, ContractHashError, "/content_hash")

    @staticmethod
    def structural_classes() -> tuple[type, ...]:
        return (
            models.MeasurementCatalog,
            models.MeasurementDefinition,
            Authority,
            ProvenanceSource,
            RepresentationSpec,
            PayloadSpec,
            UnitSpec,
            models.CoordinateSpec,
            models.AxisSpec,
            models.NumericSpec,
            models.EnumerationSpec,
            models.EnumerationMember,
            models.FreshnessSpec,
            models.ApplicabilitySelector,
        )

    def test_invalid_catalog_constructs_no_models(self) -> None:
        from xplane_fdau.measurements import _catalog_io
        from xplane_fdau.measurements import io as catalog_io

        cases: list[tuple[dict[str, Any], type[FDAUContractError], str]] = []
        for error, field, value in [
            (ContractShapeError, "title", []),
            (CanonicalJSONError, "title", None),
            (ContractHashError, "content_hash", "0" * 64),
            (ContractValidationError, "title", ""),
        ]:
            raw = raw_pair()
            raw["definitions"][1][field] = value
            if error is ContractValidationError:
                raw["definitions"][1] = signed(raw["definitions"][1])
                raw = signed_catalog(raw)
            cases.append((raw, error, "/definitions/1/" + field))
        for raw, error, path in cases:
            data = json.dumps(raw)
            with self.subTest(error=error), ExitStack() as stack:
                guards = [
                    stack.enter_context(mock.patch.object(cls, "__init__", autospec=True, side_effect=AssertionError("premature model construction")))
                    for cls in self.structural_classes()
                ]
                guards.extend(
                    stack.enter_context(
                        mock.patch.object(catalog_io if name == "_catalog_build" else _catalog_io, name, side_effect=AssertionError("premature builder"))
                    )
                    for name in ("_catalog_build", "_definition_entry_build")
                )
                self.assertFailure(data, error, path)
                self.assertTrue(all(guard.call_count == 0 for guard in guards))

    def test_build_barrier_detects_direct_constructor_bypass(self) -> None:
        from xplane_fdau.measurements import _catalog_io
        from xplane_fdau.measurements import io as catalog_io

        def premature(_: object) -> None:
            Authority(authority_id="test.early", authority_revision=1)

        with ExitStack() as stack:
            for cls in self.structural_classes():
                stack.enter_context(mock.patch.object(cls, "__init__", autospec=True, side_effect=AssertionError("premature model construction")))
            for name in ("_catalog_build", "_definition_entry_build"):
                stack.enter_context(
                    mock.patch.object(catalog_io if name == "_catalog_build" else _catalog_io, name, side_effect=AssertionError("premature builder"))
                )
            stack.enter_context(mock.patch.object(catalog_io, "_catalog_hashes", side_effect=premature))
            with self.assertRaisesRegex(AssertionError, "premature model construction"):
                self.loads(GOLDEN_CATALOG)

    def test_valid_catalog_reaches_model_construction(self) -> None:
        with ExitStack() as stack:
            guards = [stack.enter_context(mock.patch.object(cls, "__init__", autospec=True, side_effect=cls.__init__)) for cls in self.structural_classes()]
            value = self.loads(GOLDEN_CATALOG)
            self.assertGreater(guards[0].call_count, 0)
            self.assertGreater(guards[1].call_count, 0)
            self.assertEqual(GOLDEN_CATALOG, self.dumps(value))

    def test_numeric_domains_and_negative_zero(self) -> None:
        value = catalog(
            definitions=[
                definition(representation=RepresentationSpec(kind="real"), numeric=models.NumericSpec(storage_precision_bits=64, resolution=1.0, minimum=-0.0))
            ]
        )
        data = self.dumps(value)
        self.assertIn(b'"minimum":0.0', data)
        self.assertEqual(value.content_hash, self.loads(data).content_hash)
        self.assertFailure(data.replace(b'"resolution":1.0', b'"resolution":1'), ContractShapeError, "/definitions/0/numeric/resolution")
        for token in (b"1e999", b"1e-999"):
            self.assertFailure(data.replace(b'"resolution":1.0', b'"resolution":' + token), CanonicalJSONError, "/definitions/0/numeric/resolution")

    def test_streams_remain_owned_and_io_errors_propagate(self) -> None:
        class Nonseekable(io.BytesIO):
            @override
            def seek(self, *args: Any, **kwargs: Any) -> int:
                raise AssertionError("seek forbidden")

        stream = Nonseekable(GOLDEN_CATALOG)
        value = measurements.load_measurement_catalog_v1(stream)
        self.assertFalse(stream.closed)
        output = Nonseekable()
        measurements.dump_measurement_catalog_v1(value, output)
        self.assertEqual(GOLDEN_CATALOG, output.getvalue())
        self.assertFalse(output.closed)
        bad = Nonseekable(b"{}")
        with self.assertRaises(FDAUContractError):
            measurements.load_measurement_catalog_v1(bad)
        self.assertFalse(bad.closed)
        for stream in (io.StringIO("{}"), "path.json"):
            with self.assertRaises((TypeError, ContractShapeError)):
                measurements.load_measurement_catalog_v1(cast(Any, stream))
        with self.assertRaises((TypeError, ContractShapeError)):
            measurements.dump_measurement_catalog_v1(value, cast(Any, io.StringIO()))
        with self.assertRaises(ContractShapeError):
            self.dumps(cast(Any, {}))
        for operation in (
            lambda stream: measurements.load_measurement_catalog_v1(stream),
            lambda stream: measurements.dump_measurement_catalog_v1(value, stream),
        ):
            stream = mock.Mock()
            stream.read.side_effect = OSError("read failed")
            stream.write.side_effect = OSError("write failed")
            with self.assertRaises(OSError):
                operation(stream)

    def test_limits_and_deep_input_fail_with_contract_errors(self) -> None:
        raw = json.loads(GOLDEN_CATALOG)
        raw["provenance"] *= 257
        self.assertFailure(raw, ContractShapeError, "/provenance")
        deep = "[" * 1500 + "0" + "]" * 1500
        with self.assertRaises(FDAUContractError):
            self.loads(deep)

    def test_root_shape_order_precedes_later_definition_shape(self) -> None:
        raw = raw_pair()
        raw["authority"] = []
        del raw["definitions"][1]["title"]
        self.assertFailure(raw, ContractShapeError, "/authority")

    def test_all_representation_branches_round_trip(self) -> None:
        variants: list[dict[str, Any]] = []
        for kind in ("boolean", "integer", "real", "string", "enumeration", "vector", "referenced_bytes"):
            rep: dict[str, Any] = {"kind": kind}
            if kind == "vector":
                rep["length"] = 2
            elif kind == "referenced_bytes":
                rep["payload"] = PayloadSpec(allowed_media_types=["application/octet-stream"], allowed_storage_roles=["test.raw"])
            variants.append(dict(representation=RepresentationSpec(**rep)))
        for kind in ("fixed_array", "variable_array"):
            for scalar in ("boolean", "integer", "real", "string", "enumeration"):
                rep = dict(kind=kind, element_representation=scalar)
                rep.update(length=2) if kind == "fixed_array" else rep.update(minimum_length=0, maximum_length=2)
                variants.append(dict(representation=RepresentationSpec(**rep)))
        for fields in variants:
            rep = fields["representation"]
            scalar = rep.element_representation if rep.kind in ("fixed_array", "variable_array") else rep.kind
            if scalar in ("integer", "real", "vector"):
                fields["numeric"] = models.NumericSpec(storage_precision_bits=32, resolution=1 if scalar == "integer" else 1.0)
            elif scalar == "enumeration":
                fields["enumeration"] = models.EnumerationSpec(members=[models.EnumerationMember(code="test.member", label="Member", kind="known")])
            with self.subTest(kind=str(rep.kind), scalar=str(scalar)):
                value = catalog(definitions=[definition(**fields)])
                self.assertEqual(value, self.loads(self.dumps(value)))
                self.assertEqual(value.content_hash, self.loads(self.dumps(value)).content_hash)

    def test_dump_completes_short_nonseekable_binary_writes(self) -> None:
        class ShortWriter(io.RawIOBase):
            def __init__(self) -> None:
                super().__init__()
                self.data = bytearray()

            @override
            def writable(self) -> bool:
                return True

            @override
            def write(self, data: Any) -> int:
                accepted = min(7, len(data))
                self.data.extend(data[:accepted])
                return accepted

        stream = ShortWriter()
        self.addCleanup(stream.close)
        measurements.dump_measurement_catalog_v1(catalog(), cast(Any, stream))
        self.assertEqual(GOLDEN_CATALOG, bytes(stream.data))
        self.assertFalse(stream.closed)

    def test_dump_no_progress_fails_without_closing_stream(self) -> None:
        class NoProgress(io.RawIOBase):
            def __init__(self, result: int | None) -> None:
                super().__init__()
                self.result = result
                self.calls = 0

            @override
            def write(self, data: Any) -> int | None:
                self.calls += 1
                if self.calls > 1:
                    raise AssertionError("retried a write without progress")
                return self.result

        for count in (0, None, -1, 2**31, True):
            stream = NoProgress(count)
            self.addCleanup(stream.close)
            with self.subTest(count=count), self.assertRaises(OSError):
                measurements.dump_measurement_catalog_v1(catalog(), cast(Any, stream))
            self.assertFalse(stream.closed)
