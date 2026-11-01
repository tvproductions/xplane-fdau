"""Independent identity fixtures and strict staged measurement entry reading."""

from __future__ import annotations

import dataclasses
import hashlib
import inspect
import json
import subprocess
import sys
import unittest
from pathlib import Path
from types import MappingProxyType
from typing import Any, cast, override
from unittest import mock

from xplane_fdau.contracts import CanonicalJSONError, ContractHashError, ContractParseError, ContractShapeError, ContractValidationError, FDAUContractError
from xplane_fdau.contracts._content_hash import _definition_preimage
from xplane_fdau.contracts._json_parse import _NumberToken, _ObjectPairs, _parse_json_document
from xplane_fdau.contracts.provenance import Authority, ProvenanceSource
from xplane_fdau.contracts.values import PayloadSpec, RepresentationSpec, UnitSpec
from xplane_fdau.measurements import models

FAMILY = "https://tvproductions.github.io/xplane-fdau/contracts/measurement-catalog"
# Literal fixture: independent of every production projection and encoder.
BODY = (
    b'{"allowed_quality":[],"allowed_validity":["unknown"],"applicability":[],'
    b'"authority":{"authority_id":"test.authority","authority_revision":1},'
    b'"coordinates":{"kind":"not_applicable"},"definition_id":"test.boolean",'
    b'"definition_revision":1,"description":"Boolean meaning","discontinuity_policy":"preserve",'
    b'"freshness":{"fresh_for_ns":0},"interpolation_policy":"prohibited","limitations":[],'
    b'"provenance":[{"scope":"Synthetic","source_id":"test.source","source_revision":1}],'
    b'"quantity_id":"test.state","representation":{"kind":"boolean"},'
    b'"sensitivity":"unknown","title":"Boolean","unit":{"kind":"unitless"}}'
)
PREIMAGE = b'{"contract_family":"https://tvproductions.github.io/xplane-fdau/contracts/measurement-catalog","definition":' + BODY + b',"schema_version":1}\n'
DIGEST = hashlib.sha256(PREIMAGE).hexdigest()
ENTRY = (
    b'{"allowed_quality":[],"allowed_validity":["unknown"],"applicability":[],'
    b'"authority":{"authority_id":"test.authority","authority_revision":1},'
    b'"content_hash":"f54509db50da50bd1c72c59ed3b4ce736d97ff31c16cdc07e5790ccd55a745b9",'
    b'"coordinates":{"kind":"not_applicable"},"definition_id":"test.boolean",'
    b'"definition_revision":1,"description":"Boolean meaning","discontinuity_policy":"preserve",'
    b'"freshness":{"fresh_for_ns":0},"interpolation_policy":"prohibited","limitations":[],'
    b'"provenance":[{"scope":"Synthetic","source_id":"test.source","source_revision":1}],'
    b'"quantity_id":"test.state","representation":{"kind":"boolean"},'
    b'"sensitivity":"unknown","title":"Boolean","unit":{"kind":"unitless"}}\n'
)


def definition(**changes: Any) -> models.MeasurementDefinition:
    fields: dict[str, Any] = dict(
        definition_id="test.boolean",
        definition_revision=1,
        authority=Authority(authority_id="test.authority", authority_revision=1),
        provenance=[ProvenanceSource(source_id="test.source", scope="Synthetic", source_revision=1)],
        title="Boolean",
        description="Boolean meaning",
        limitations=[],
        quantity_id="test.state",
        representation=RepresentationSpec(kind="boolean"),
        unit=UnitSpec(kind="unitless"),
        coordinates=models.CoordinateSpec(kind="not_applicable"),
        freshness=models.FreshnessSpec(fresh_for_ns=0),
        interpolation_policy="prohibited",
        discontinuity_policy="preserve",
        allowed_validity=["unknown"],
        allowed_quality=[],
        sensitivity="unknown",
        applicability=[],
    )
    return models.MeasurementDefinition(**(fields | changes))


def signed(fields: dict[str, Any]) -> dict[str, Any]:
    # Test inputs here have only ASCII text, integer values and simple exact floats.
    body = {key: value for key, value in fields.items() if key != "content_hash"}
    data = (
        json.dumps(dict(contract_family=FAMILY, schema_version=1, definition=body), sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
        + b"\n"
    )
    return fields | {"content_hash": hashlib.sha256(data).hexdigest()}


class MeasurementDefinitionIOTests(unittest.TestCase):
    @override
    def setUp(self) -> None:
        self.assertTrue(Path(models.__file__).with_name("_definition_io.py").is_file(), "private staged definition reader is absent")
        from xplane_fdau.measurements import _definition_io

        self.io = _definition_io

    def assertFailure(self, value: object, error: type[FDAUContractError], path: str, *, identity: str = "test.boolean") -> None:
        with self.assertRaises(error) as caught:
            self.io._measurement_definition_from_wire(value, path="/definitions/2", source="definition.json")
        self.assertEqual("/definitions/2" + path, caught.exception.path)
        self.assertEqual("definition.json", caught.exception.source)
        self.assertIsNone(caught.exception.line)
        self.assertIsNone(caught.exception.column)
        self.assertEqual(FAMILY, caught.exception.contract_family)
        self.assertEqual(identity, caught.exception.identity)

    def test_literal_boolean_bytes_hash_and_preimage(self) -> None:
        value = definition()
        self.assertEqual(ENTRY, self.io._measurement_definition_bytes(value))
        self.assertEqual(DIGEST, value.content_hash)
        self.assertEqual(PREIMAGE, _definition_preimage(FAMILY, self.io._measurement_definition_wire(value, include_hash=False)))
        self.assertEqual(value, self.io._measurement_definition_from_wire(_parse_json_document(ENTRY)))

    def test_round_trips_every_representation_and_metadata(self) -> None:
        member = models.EnumerationMember(code="test.active", label="Active", kind="known")
        cases: list[dict[str, Any]] = [dict(representation=RepresentationSpec(kind=kind)) for kind in ("boolean", "string")]
        cases += [
            dict(representation=RepresentationSpec(kind="integer"), numeric=models.NumericSpec(storage_precision_bits=64, resolution=1, minimum=-2, maximum=2)),
            dict(
                representation=RepresentationSpec(kind="real"),
                numeric=models.NumericSpec(storage_precision_bits=64, resolution=0.5, minimum=-2.0, maximum=2.0),
                unit=UnitSpec(kind="unit", quantity_id="test.state", unit_id="test.unit"),
            ),
            dict(
                representation=RepresentationSpec(kind="vector", length=2),
                numeric=models.NumericSpec(storage_precision_bits=64, resolution=0.5),
                coordinates=models.CoordinateSpec(
                    kind="applicable",
                    reference_frame_id="test.frame",
                    datum_id="test.datum",
                    handedness="right",
                    axes=[
                        models.AxisSpec(axis_id="test.x", direction="x", sign_convention="positive"),
                        models.AxisSpec(axis_id="test.y", direction="y", sign_convention="positive"),
                    ],
                ),
            ),
            dict(representation=RepresentationSpec(kind="enumeration"), enumeration=models.EnumerationSpec(members=[member])),
            dict(
                representation=RepresentationSpec(
                    kind="referenced_bytes", payload=PayloadSpec(allowed_media_types=["application/octet-stream"], allowed_storage_roles=["test.evidence"])
                )
            ),
        ]
        for kind in ("fixed_array", "variable_array"):
            for element in ("boolean", "string", "enumeration", "integer", "real"):
                rep = RepresentationSpec(
                    kind=kind, element_representation=element, **({"length": 2} if kind == "fixed_array" else {"minimum_length": 0, "maximum_length": 2})
                )
                metadata: dict[str, Any] = {}
                if element == "enumeration":
                    metadata["enumeration"] = models.EnumerationSpec(members=[member])
                if element in ("integer", "real"):
                    metadata["numeric"] = models.NumericSpec(storage_precision_bits=32, resolution=1 if element == "integer" else 0.5)
                cases.append(dict(representation=rep, **metadata))
        for changes in cases:
            with self.subTest(changes=changes):
                value = definition(**changes, applicability=[models.ApplicabilitySelector(class_id="test.aircraft", value="Synthetic")])
                for wire in (self.io._measurement_definition_wire(value), _parse_json_document(self.io._measurement_definition_bytes(value))):
                    self.assertEqual(value, self.io._measurement_definition_from_wire(wire))

    def test_all_semantic_fields_affect_identity(self) -> None:
        value = definition()
        changes = dict(
            definition_id="test.other",
            definition_revision=2,
            authority=Authority(authority_id="test.other", authority_revision=1),
            provenance=[ProvenanceSource(source_id="test.other", scope="Synthetic", source_revision=1)],
            title="Other",
            description="Other",
            limitations=["Limit"],
            quantity_id="test.other",
            representation=RepresentationSpec(kind="string"),
            coordinates=models.CoordinateSpec(
                kind="applicable",
                reference_frame_id="test.frame",
                handedness="left",
                axes=[models.AxisSpec(axis_id="test.x", direction="x", sign_convention="positive")],
            ),
            freshness=models.FreshnessSpec(stale_after_ns=1),
            interpolation_policy="hold",
            discontinuity_policy="reject",
            allowed_validity=["valid"],
            allowed_quality=["stale"],
            sensitivity="public",
            applicability=[models.ApplicabilitySelector(class_id="test.aircraft", value="Synthetic")],
        )
        for name, replacement in changes.items():
            with self.subTest(field=name):
                self.assertNotEqual(value.content_hash, dataclasses.replace(value, **{name: replacement}).content_hash)
        real = definition(representation=RepresentationSpec(kind="real"), numeric=models.NumericSpec(storage_precision_bits=64, resolution=0.5, minimum=0.0))
        self.assertNotEqual(
            real.content_hash, dataclasses.replace(real, unit=UnitSpec(kind="unit", quantity_id="test.state", unit_id="test.unit")).content_hash
        )
        self.assertNotEqual(real.content_hash, dataclasses.replace(real, numeric=models.NumericSpec(storage_precision_bits=32, resolution=0.5)).content_hash)
        enum = definition(
            representation=RepresentationSpec(kind="enumeration"),
            enumeration=models.EnumerationSpec(members=[models.EnumerationMember(code="test.a", label="A", kind="known")]),
        )
        self.assertNotEqual(
            enum.content_hash,
            dataclasses.replace(
                enum, enumeration=models.EnumerationSpec(members=[models.EnumerationMember(code="test.a", label="B", kind="known")])
            ).content_hash,
        )
        self.assertEqual(
            real.content_hash, dataclasses.replace(real, numeric=models.NumericSpec(storage_precision_bits=64, resolution=0.5, minimum=-0.0)).content_hash
        )

    def test_order_mutation_and_cached_read_only_slot(self) -> None:
        provenance = [
            ProvenanceSource(source_id="test.a", scope="A", source_version="1"),
            ProvenanceSource(source_id="test.b", scope="B", source_version="2", locator="test:source", sha256="a" * 64),
        ]
        limitations = ["A", "B"]
        value = definition(provenance=provenance, limitations=limitations)
        before = self.io._measurement_definition_bytes(value)
        self.assertNotEqual(value.content_hash, dataclasses.replace(value, provenance=list(reversed(provenance))).content_hash)
        self.assertNotEqual(value.content_hash, dataclasses.replace(value, limitations=list(reversed(limitations))).content_hash)
        provenance.clear()
        limitations.clear()
        self.assertEqual(before, self.io._measurement_definition_bytes(value))
        with mock.patch("xplane_fdau.measurements.models._definition_content_hash", side_effect=AssertionError("hash recomputed")):
            self.assertEqual(value.content_hash, value.content_hash)
            self.assertEqual(before, self.io._measurement_definition_bytes(value))
        self.assertFalse(hasattr(value, "__dict__"))
        self.assertNotIn("content_hash", inspect.signature(models.MeasurementDefinition).parameters)
        with self.assertRaises((AttributeError, TypeError)):
            cast(Any, value).content_hash = "b" * 64
        with self.assertRaises(TypeError):
            definition(content_hash="b" * 64)

    def test_object_order_and_whitespace_do_not_affect_identity(self) -> None:
        wire = json.loads(ENTRY)
        reordered = dict(reversed(list(wire.items())))
        parsed = _parse_json_document(json.dumps(reordered, indent=3))
        self.assertEqual(ENTRY, self.io._measurement_definition_bytes(self.io._measurement_definition_from_wire(parsed)))

    def test_stage_precedence_and_build_barrier(self) -> None:
        base: dict[str, Any] = json.loads(ENTRY)
        numeric = base | {"representation": {"kind": "real"}, "numeric": {"storage_precision_bits": 64, "resolution": 0.0}}
        cases = [
            (numeric, ContractHashError, "/content_hash"),
            (signed(numeric), ContractValidationError, "/numeric/resolution"),
            (numeric | {"applicability": [{"class_id": "test.class"}]}, ContractShapeError, "/applicability/0/value"),
            (numeric | {"title": "e\u0301"}, CanonicalJSONError, "/title"),
        ]
        with mock.patch.object(self.io, "_definition_entry_build", side_effect=AssertionError("premature model build")):
            for wire, error, path in cases:
                with self.subTest(error=error):
                    self.assertFailure(_parse_json_document(json.dumps(wire)), error, path)
        with mock.patch.object(self.io, "_definition_entry_build", wraps=self.io._definition_entry_build) as build:
            self.io._measurement_definition_from_wire(_parse_json_document(ENTRY))
            build.assert_called_once()
            self.assertIs(type(build.call_args.args[0]["definition_revision"]), int)
            self.assertIs(type(build.call_args.args[0]["authority"]), dict)

    def test_strict_shape_and_domains(self) -> None:
        base: dict[str, Any] = json.loads(ENTRY)
        for changes, error, path in [
            ({"definition_revision": 1.0}, ContractShapeError, "/definition_revision"),
            ({"title": 1}, ContractShapeError, "/title"),
            ({"title": None}, CanonicalJSONError, "/title"),
            ({"title": "\ud800"}, CanonicalJSONError, "/title"),
            ({"definition_revision": 2**63}, CanonicalJSONError, "/definition_revision"),
            ({"representation": {"kind": "boolean", "length": 1}}, ContractShapeError, "/representation/length"),
            ({"content_hash": "bad"}, ContractValidationError, "/content_hash"),
            ({"authority": {"authority_id": "test.authority", "authority_revision": True}}, ContractShapeError, "/authority/authority_revision"),
            ({"other/~": 1}, ContractShapeError, "/other~1~0"),
        ]:
            with self.subTest(changes=changes):
                self.assertFailure(_parse_json_document(json.dumps(base | changes)), error, path)
        missing = dict(base)
        del missing["content_hash"]
        self.assertFailure(missing, ContractShapeError, "/content_hash")
        malformed = base | {"content_hash": "bad", "authority": {"authority_id": "invalid", "authority_revision": 1}}
        self.assertFailure(malformed, ContractValidationError, "/content_hash")
        with self.assertRaises(ContractParseError):
            self.io._measurement_definition_from_wire(_parse_json_document(ENTRY[:-2] + b',"title":"duplicate"}'))

    def test_numeric_lexical_overflow_underflow_and_parity(self) -> None:
        real = definition(representation=RepresentationSpec(kind="real"), numeric=models.NumericSpec(storage_precision_bits=64, resolution=0.5))
        data = self.io._measurement_definition_bytes(real)
        for token, error in ((b"1e-9999", CanonicalJSONError), (b"1e9999", CanonicalJSONError), (b"1", ContractShapeError)):
            self.assertFailure(_parse_json_document(data.replace(b'"resolution":0.5', b'"resolution":' + token)), error, "/numeric/resolution")
        invalid = json.loads(data)
        invalid["numeric"]["resolution"] = 0.0
        self.assertFailure(signed(invalid), ContractValidationError, "/numeric/resolution")
        with self.assertRaises(ContractValidationError) as caught:
            models.NumericSpec(storage_precision_bits=64, resolution=0.0)
        self.assertEqual("/resolution", caught.exception.path)
        shape = self.io._definition_entry_shape(_parse_json_document(data))
        self.assertIsInstance(cast(dict[str, object], shape["numeric"])["resolution"], _NumberToken)
        materialized = self.io._definition_entry_domains(shape)
        self.assertIs(type(cast(dict[str, object], materialized["numeric"])["resolution"]), float)

    def test_nested_constructor_reader_error_parity(self) -> None:
        base: dict[str, Any] = json.loads(ENTRY)
        # Each independently signed invalid entry must report the constructor's
        # local path, with only its containing definition field prepended.
        cases: list[tuple[str, Any, dict[str, Any], str]] = [
            ("authority", Authority, dict(authority_id="invalid", authority_revision=1), "/authority_id"),
            ("provenance", ProvenanceSource, dict(source_id="test.source", scope="", source_revision=1), "/scope"),
            ("coordinates", models.CoordinateSpec, dict(kind="applicable", reference_frame_id="invalid", handedness="right", axes=[]), "/reference_frame_id"),
            ("freshness", models.FreshnessSpec, dict(fresh_for_ns=2, stale_after_ns=1), "/stale_after_ns"),
            ("applicability", models.ApplicabilitySelector, dict(class_id="invalid", value="A"), "/class_id"),
        ]
        for name, cls, fields, local_path in cases:
            with self.subTest(field=name):
                with self.assertRaises(ContractValidationError) as constructor_error:
                    cls(**fields)
                self.assertEqual(local_path, constructor_error.exception.path)
                value = base | {name: [fields] if name in ("provenance", "applicability") else fields}
                self.assertFailure(signed(value), ContractValidationError, "/" + name + ("/0" if name in ("provenance", "applicability") else "") + local_path)
        for field, owned, raw, local_path in [
            ("axes", models.AxisSpec, dict(axis_id="test.x", direction="", sign_convention="positive"), "/direction"),
            ("members", models.EnumerationMember, dict(code="test.a", label="", kind="known"), "/label"),
        ]:
            with self.subTest(field=field):
                with self.assertRaises(ContractValidationError) as constructor_error:
                    owned(**raw)
                self.assertEqual(local_path, constructor_error.exception.path)
                if field == "axes":
                    wire = base | {"coordinates": dict(kind="applicable", reference_frame_id="test.frame", handedness="right", axes=[raw])}
                    path = "/coordinates/axes/0" + local_path
                else:
                    wire = base | {"representation": {"kind": "enumeration"}, "enumeration": {"members": [raw]}}
                    path = "/enumeration/members/0" + local_path
                self.assertFailure(signed(wire), ContractValidationError, path)

    def test_axis_order_and_nested_provenance_affect_hash(self) -> None:
        axes = [
            models.AxisSpec(axis_id="test.x", direction="x", sign_convention="positive"),
            models.AxisSpec(axis_id="test.y", direction="y", sign_convention="positive"),
        ]
        coordinate = models.CoordinateSpec(kind="applicable", reference_frame_id="test.frame", handedness="right", axes=axes)
        value = definition(
            representation=RepresentationSpec(kind="vector", length=2),
            numeric=models.NumericSpec(storage_precision_bits=64, resolution=1.0),
            coordinates=coordinate,
        )
        self.assertNotEqual(value.content_hash, dataclasses.replace(value, coordinates=dataclasses.replace(coordinate, axes=list(reversed(axes)))).content_hash)
        before = self.io._measurement_definition_bytes(value)
        axes.clear()
        self.assertEqual(before, self.io._measurement_definition_bytes(value))
        source = value.provenance[0]
        for changes in (dict(scope="Other"), dict(source_revision=2), dict(locator="test:source"), dict(sha256="a" * 64)):
            with self.subTest(changes=changes):
                self.assertNotEqual(value.content_hash, dataclasses.replace(value, provenance=[dataclasses.replace(source, **changes)]).content_hash)
        self.assertNotEqual(value.content_hash, dataclasses.replace(value, authority=dataclasses.replace(value.authority, authority_revision=2)).content_hash)

    def test_parse_precedence_and_known_bounded_error_context(self) -> None:
        pairs = _ObjectPairs(
            (("definition_id", "test.boolean"), ("definition_revision", _NumberToken("99999999999999999999", False)), ("title", "A"), ("title", "B"))
        )
        self.assertFailure(pairs, ContractParseError, "/title")
        # Mixed raw dictionaries must retain duplicate detection in nested parser objects.
        self.assertFailure(
            dict(json.loads(ENTRY), authority=_ObjectPairs((("authority_id", "test.a"), ("authority_id", "test.b")))),
            ContractParseError,
            "/authority/authority_id",
        )
        mixed = _ObjectPairs(
            tuple(
                dict(json.loads(ENTRY), authority={"authority_id": "test.a", "authority_revision": _ObjectPairs((("duplicate", 1), ("duplicate", 2)))}).items()
            )
        )
        with self.assertRaises(FDAUContractError) as mixed_error:
            self.io._measurement_definition_from_wire(mixed)
        self.assertIs(type(mixed_error.exception), ContractParseError)
        self.assertEqual("/authority/authority_revision/duplicate", mixed_error.exception.path)
        with self.assertRaises(ContractShapeError) as unknown:
            self.io._measurement_definition_from_wire({}, source="empty.json")
        self.assertIsNone(unknown.exception.identity)

    def test_error_identity_is_bounded(self) -> None:
        with self.assertRaises(ContractHashError) as bounded:
            self.io._measurement_definition_from_wire(dict(json.loads(ENTRY), definition_id="a" * 400))
        self.assertEqual("a" * 160, bounded.exception.identity)

    def test_domain_limits_and_depth_are_checked_before_hash(self) -> None:
        # The exact entry schema cannot reach arbitrary depth. Exercise the
        # domain stage directly to guard its generic container defense.
        nested: object = "leaf"
        for _ in range(64):
            nested = [nested]
        for fields, path in (({"title": nested}, "/title" + "/0" * 63), ({"title": ["x"] * 65536}, "/title")):
            with self.subTest(path=path):
                with self.assertRaises(CanonicalJSONError) as caught:
                    self.io._definition_entry_domains(fields)
                self.assertEqual(path, caught.exception.path)
        base: dict[str, Any] = json.loads(ENTRY)
        self.assertFailure(base | {"title": "e\u0301", "applicability": [{"class_id": "test.a"}]}, ContractShapeError, "/applicability/0/value")
        self.assertFailure(base | {"content_hash": None, "title": "e\u0301"}, CanonicalJSONError, "/content_hash")
        self.assertFailure(signed(base | {"definition_id": "invalid"}) | {"content_hash": "bad"}, ContractValidationError, "/definition_id", identity="invalid")

    def test_reader_rejects_non_json_tag_and_nested_mapping_substitutes(self) -> None:
        base: dict[str, Any] = json.loads(ENTRY)
        for changes, path in (
            ({"interpolation_policy": models.InterpolationPolicy.PROHIBITED}, "/interpolation_policy"),
            ({"authority": MappingProxyType(base["authority"])}, "/authority"),
            ({"representation": {"kind": models.ValidityState.UNKNOWN}}, "/representation/kind"),
        ):
            with self.subTest(path=path):
                with self.assertRaises(FDAUContractError) as caught:
                    self.io._measurement_definition_from_wire(base | changes)
                self.assertIs(type(caught.exception), ContractShapeError)
                self.assertEqual(path, caught.exception.path)

    def test_parser_accepted_deep_input_preserves_shape_precedence(self) -> None:
        deep_json = "[" * 600 + "0" + "]" * 600
        # The unchanged parser accepts these documents. Shape must win even
        # though projection of a rejected title would exceed Python's stack.
        incomplete = _parse_json_document('{"title":' + deep_json + "}")
        complete = _parse_json_document(ENTRY.replace(b'"title":"Boolean"', b'"title":' + deep_json.encode("ascii")))
        for value, path in ((incomplete, "/definition_id"), (complete, "/title")):
            with self.subTest(path=path), mock.patch.object(self.io, "_definition_entry_build", side_effect=AssertionError("premature model build")):
                with self.assertRaises(Exception) as caught:
                    self.io._measurement_definition_from_wire(value, source="deep.json", path="/definitions/2")
                self.assertIs(type(caught.exception), ContractShapeError)
                error = cast(FDAUContractError, caught.exception)
                self.assertEqual("/definitions/2" + path, error.path)
                self.assertEqual("deep.json", error.source)

    def test_deep_domain_preprocessing_reaches_its_depth_guard(self) -> None:
        nested = _parse_json_document("[" * 600 + "0" + "]" * 600)
        with self.assertRaises(Exception) as caught:
            self.io._definition_entry_domains({"title": nested})
        self.assertIs(type(caught.exception), CanonicalJSONError)
        self.assertEqual("/title" + "/0" * 63, cast(FDAUContractError, caught.exception).path)

    def test_stack_safe_duplicates_still_precede_shape_and_domains(self) -> None:
        # A raw dictionary may mix parser objects and tuples. Scan the whole
        # input before rejecting a missing identity or a wrong title shape.
        nested: object = _ObjectPairs((("duplicate", 1), ("duplicate", 2)))
        for index in range(1600):
            nested = [nested] if index % 2 else (nested,)
        with self.assertRaises(Exception) as caught:
            self.io._measurement_definition_from_wire({"title": nested}, source="deep.json")
        self.assertIs(type(caught.exception), ContractParseError)
        error = cast(FDAUContractError, caught.exception)
        self.assertEqual("/title" + "/0" * 1600 + "/duplicate", error.path)
        self.assertEqual("deep.json", error.source)
        # Even without a duplicate, raw deep containers must reach shape.
        plain: object = 0
        for _ in range(1600):
            plain = [plain]
        with self.assertRaises(Exception) as wrong_shape:
            self.io._measurement_definition_from_wire({"title": plain})
        self.assertIs(type(wrong_shape.exception), ContractShapeError)
        self.assertEqual("/definition_id", cast(FDAUContractError, wrong_shape.exception).path)

    def test_both_package_import_orders_in_fresh_processes(self) -> None:
        for order in (("contracts", "measurements"), ("measurements", "contracts")):
            code = "; ".join(f"import xplane_fdau.{name}" for name in order)
            result = subprocess.run([sys.executable, "-c", code], capture_output=True, shell=False, check=False)
            self.assertEqual(0, result.returncode, result.stderr.decode("utf-8", errors="replace"))
