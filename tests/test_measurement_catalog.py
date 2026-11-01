"""Catalog ownership, immutable identity and ordered-pair rejection."""

from __future__ import annotations

import dataclasses
import inspect
import json
import unittest
from typing import Any, override

from tests.measurement_catalog_support import CATALOG_HASH, CATALOG_PREIMAGE, DEFINITION_HASH, GOLDEN_CATALOG, catalog, definition
from xplane_fdau.contracts import Authority, CanonicalJSONError, ContractShapeError, ContractValidationError, ProvenanceSource
from xplane_fdau.measurements import models


class MeasurementCatalogTests(unittest.TestCase):
    @override
    def setUp(self) -> None:
        self.assertTrue(hasattr(models, "MeasurementCatalog"), "immutable catalog is missing")

    def test_catalog_signature_and_immutability(self) -> None:
        names = ["contract_family", "schema_version", "catalog_id", "catalog_revision", "authority", "provenance", "definitions", "title", "scope"]
        signature = inspect.signature(models.MeasurementCatalog)
        self.assertEqual(names, list(signature.parameters))
        self.assertTrue(all(p.kind is inspect.Parameter.KEYWORD_ONLY for p in signature.parameters.values()))
        entries = [definition()]
        sources = [ProvenanceSource(source_id="test.source", scope="Synthetic", source_revision=1)]
        value = catalog(definitions=entries, provenance=sources)
        entries.clear()
        sources.clear()
        self.assertEqual(1, len(value.definitions))
        self.assertIsInstance(value.definitions, tuple)
        self.assertIsInstance(value.provenance, tuple)
        self.assertFalse(hasattr(value, "__dict__"))
        with self.assertRaises(dataclasses.FrozenInstanceError):
            value.catalog_id = "test.changed"
        with self.assertRaises(TypeError):
            catalog(content_hash="0" * 64)

    def test_catalog_metadata_and_omission(self) -> None:
        from xplane_fdau.measurements._catalog_io import _measurement_catalog_wire

        self.assertNotIn("title", _measurement_catalog_wire(catalog()))
        self.assertNotIn("scope", _measurement_catalog_wire(catalog()))
        catalog(catalog_revision=9223372036854775807, title="a" * 256, scope="a" * 2048)
        cases = [
            ("contract_family", "test.other", ContractValidationError),
            ("schema_version", 2, ContractValidationError),
            ("schema_version", True, ContractShapeError),
            ("catalog_id", "bad", ContractValidationError),
            ("catalog_revision", 0, ContractValidationError),
            ("catalog_revision", True, ContractShapeError),
            ("catalog_revision", 2**63, CanonicalJSONError),
            ("authority", {}, ContractShapeError),
            ("provenance", [], ContractValidationError),
            ("definitions", [], ContractValidationError),
            ("title", None, CanonicalJSONError),
            ("scope", None, CanonicalJSONError),
            ("title", "", ContractValidationError),
            ("scope", "", ContractValidationError),
            ("title", "a" * 257, ContractValidationError),
            ("scope", "a" * 2049, ContractValidationError),
            ("title", "e\u0301", CanonicalJSONError),
            ("definitions", set(), ContractShapeError),
        ]
        for name, value, error in cases:
            with self.subTest(name=name, value=repr(value)[:50]), self.assertRaises(error) as caught:
                catalog(**{name: value})
            self.assertEqual("/" + name, caught.exception.path)
        for name, value, path in [("definitions", [{}], "/definitions/0"), ("provenance", [{}], "/provenance/0")]:
            with self.assertRaises(ContractShapeError) as caught:
                catalog(**{name: value})
            self.assertEqual(path, caught.exception.path)

    def test_provenance_order_identity_and_bounds(self) -> None:
        sources = [ProvenanceSource(source_id=f"test.s{i}", scope="Synthetic", source_revision=1) for i in range(256)]
        value = catalog(provenance=sources)
        self.assertEqual(tuple(sources), value.provenance)
        with self.assertRaises(ContractShapeError) as caught:
            catalog(provenance=[*sources, sources[0]])
        self.assertEqual("/provenance", caught.exception.path)
        with self.assertRaises(ContractValidationError) as caught:
            catalog(provenance=[sources[0], sources[0]])
        self.assertEqual("/provenance/1", caught.exception.path)

    def test_definition_pair_order(self) -> None:
        first = definition(definition_id="test.a", definition_revision=1)
        second = definition(definition_id="test.a", definition_revision=2)
        third = definition(definition_id="test.b")
        self.assertEqual((first, second, third), catalog(definitions=[first, second, third]).definitions)
        for entries, path in [
            ([first, first], "/definitions/1/definition_revision"),
            ([second, first], "/definitions/1/definition_revision"),
            ([third, first], "/definitions/1/definition_id"),
        ]:
            original = entries.copy()
            with self.assertRaises(ContractValidationError) as caught:
                catalog(definitions=entries)
            self.assertEqual(path, caught.exception.path)
            self.assertEqual(original, entries)

    def test_catalog_hash_preimage(self) -> None:
        from xplane_fdau.contracts.canonical_json import _encode_document
        from xplane_fdau.measurements._catalog_io import _measurement_catalog_bytes, _measurement_catalog_wire

        value = catalog()
        self.assertEqual(DEFINITION_HASH, value.definitions[0].content_hash)
        self.assertEqual(CATALOG_HASH, value.content_hash)
        self.assertEqual(CATALOG_PREIMAGE, _encode_document(_measurement_catalog_wire(value, include_hash=False)))
        self.assertEqual(GOLDEN_CATALOG, _measurement_catalog_bytes(value))
        self.assertEqual(DEFINITION_HASH, json.loads(CATALOG_PREIMAGE)["definitions"][0]["content_hash"])

    def test_catalog_metadata_does_not_change_definition_identity(self) -> None:
        original = catalog()
        changed = catalog(catalog_id="test.changed", catalog_revision=2, authority=Authority(authority_id="test.other", authority_revision=2), scope="other")
        self.assertEqual(original.definitions[0].content_hash, changed.definitions[0].content_hash)
        self.assertNotEqual(original.content_hash, changed.content_hash)
        edited = catalog(definitions=[definition(title="Changed")])
        self.assertNotEqual(original.definitions[0].content_hash, edited.definitions[0].content_hash)
        self.assertNotEqual(original.content_hash, edited.content_hash)

    def test_shape_collection_limit_without_constructing_thousands_of_models(self) -> None:
        from xplane_fdau.measurements._catalog_validation import _validate_catalog_fields

        fields: dict[str, Any] = json.loads(GOLDEN_CATALOG)
        entry = fields["definitions"][0]
        fields["definitions"] = [entry] * 65535
        _validate_catalog_fields(fields, 0, wire=True)
        fields["definitions"].append(entry)
        with self.assertRaises(ContractShapeError) as caught:
            _validate_catalog_fields(fields, 0, wire=True)
        self.assertEqual("/definitions", caught.exception.path)
