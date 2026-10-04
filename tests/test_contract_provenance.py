"""C1.2 immutable authority and provenance values."""

from __future__ import annotations

import unittest
from dataclasses import fields
from typing import Any, cast

from xplane_fdau.contracts.errors import CanonicalJSONError, ContractValidationError
from xplane_fdau.contracts.provenance import (
    AdapterIdentity,
    Authority,
    ProducerIdentity,
    ProvenanceSource,
    ProviderIdentity,
    _adapter_wire,
    _authority_wire,
    _catalog_provenance,
    _producer_wire,
    _provenance_source_wire,
    _provider_wire,
)


class ProvenanceTests(unittest.TestCase):
    def test_all_provenance_models_have_exact_immutable_keyword_fields(self) -> None:
        cases = (
            (Authority(authority_id="test.owner", authority_revision=1), ("authority_id", "authority_revision")),
            (
                ProvenanceSource(source_id="test.manual", scope="source", source_revision=1),
                ("source_id", "scope", "source_revision", "source_version", "locator", "sha256"),
            ),
            (
                ProducerIdentity(implementation_id="test.fdau", implementation_version="1", producer_instance_id="12345678-1234-1234-8234-123456789abc"),
                ("implementation_id", "implementation_version", "producer_instance_id", "source_revision"),
            ),
            (ProviderIdentity(provider_family_id="test.xplm", provider_version="1"), ("provider_family_id", "provider_version")),
            (AdapterIdentity(adapter_family_id="test.plugin", adapter_version="1"), ("adapter_family_id", "adapter_version")),
        )
        for model, expected in cases:
            with self.subTest(model=type(model).__name__):
                self.assertEqual(tuple(field.name for field in fields(model)), expected)
                self.assertTrue(all(field.kw_only for field in fields(model)))
                self.assertFalse(hasattr(model, "__dict__"))
                with self.assertRaises(AttributeError):
                    setattr(model, expected[0], "changed")

    def test_locator_and_sha256_are_independently_optional(self) -> None:
        base = {"source_id": "test.manual", "scope": "source", "source_revision": 1}
        for optional in ({"locator": "manual:3"}, {"sha256": "b" * 64}):
            with self.subTest(optional=optional):
                value = cast(Any, ProvenanceSource)(**(base | optional))
                self.assertEqual(_provenance_source_wire(value), base | optional)

    def test_authority_and_provider_adapter_round_trip(self) -> None:
        for model, wire in (
            (Authority(authority_id="test.owner", authority_revision=2), _authority_wire),
            (ProviderIdentity(provider_family_id="test.xplm", provider_version="1.2"), _provider_wire),
            (AdapterIdentity(adapter_family_id="test.plugin", adapter_version="2.0"), _adapter_wire),
        ):
            with self.subTest(model=type(model).__name__):
                self.assertEqual(model, cast(Any, type(model))(**cast(Any, wire)(model)))
                self.assertFalse(hasattr(model, "__dict__"))
                with self.assertRaises((AttributeError, TypeError)):
                    setattr(model, "extra", "changed")
        with self.assertRaises(TypeError):
            cast(Any, Authority)("test.owner", 1)
        with self.assertRaises(ContractValidationError) as caught:
            Authority(authority_id="test.owner", authority_revision=0)
        self.assertEqual(caught.exception.path, "/authority_revision")

    def test_provenance_source_xor_and_optional_wire_fields(self) -> None:
        revision = ProvenanceSource(source_id="test.manual", scope="airframe", source_revision=3)
        version = ProvenanceSource(source_id="test.manual", scope="airframe", source_version="r3", locator="book:2", sha256="a" * 64)
        self.assertEqual(
            _provenance_source_wire(revision),
            {"source_id": "test.manual", "scope": "airframe", "source_revision": 3},
        )
        self.assertEqual(
            _provenance_source_wire(version),
            {"source_id": "test.manual", "scope": "airframe", "source_version": "r3", "locator": "book:2", "sha256": "a" * 64},
        )
        for value in (revision, version):
            self.assertEqual(value, cast(Any, ProvenanceSource)(**_provenance_source_wire(value)))
            self.assertFalse(hasattr(value, "__dict__"))
        for kwargs, path in (
            ({}, "/source_revision"),
            ({"source_revision": 3, "source_version": "r3"}, "/source_version"),
        ):
            with self.subTest(kwargs=kwargs):
                with self.assertRaises(ContractValidationError) as caught:
                    cast(Any, ProvenanceSource)(source_id="test.manual", scope="airframe", **kwargs)
                self.assertEqual(caught.exception.path, path)
        for kwargs, error, path in (
            ({"scope": "e\u0301"}, CanonicalJSONError, "/scope"),
            ({"scope": "x" * 1025}, ContractValidationError, "/scope"),
            ({"locator": "x" * 2049}, ContractValidationError, "/locator"),
        ):
            with self.subTest(kwargs=kwargs):
                with self.assertRaises(error) as caught:
                    cast(Any, ProvenanceSource)(**({"source_id": "test.manual", "scope": "airframe", "source_revision": 1} | kwargs))
                self.assertEqual(caught.exception.path, path)

    def test_producer_version_and_optional_source_revision(self) -> None:
        producer = ProducerIdentity(implementation_id="test.fdau", implementation_version="1.2", producer_instance_id="12345678-1234-1234-8234-123456789abc")
        self.assertEqual(
            _producer_wire(producer),
            {"implementation_id": "test.fdau", "implementation_version": "1.2", "producer_instance_id": "12345678-1234-1234-8234-123456789abc"},
        )
        with_revision = ProducerIdentity(
            implementation_id="test.fdau", implementation_version="1.2", producer_instance_id="12345678-1234-1234-8234-123456789abc", source_revision="git.abcd"
        )
        self.assertEqual(_producer_wire(with_revision)["source_revision"], "git.abcd")
        self.assertEqual(with_revision, cast(Any, ProducerIdentity)(**_producer_wire(with_revision)))
        for revision in ("bad\nrevision", "bad\u200drevision"):
            with self.subTest(revision=revision):
                with self.assertRaises(ContractValidationError) as caught:
                    ProducerIdentity(
                        implementation_id="test.fdau",
                        implementation_version="1.2",
                        producer_instance_id="12345678-1234-1234-8234-123456789abc",
                        source_revision=revision,
                    )
                self.assertEqual(caught.exception.path, "/source_revision")

    def test_catalog_provenance_preserves_order_and_rejects_duplicate_identity(self) -> None:
        first = ProvenanceSource(source_id="test.manual", scope="source", source_revision=1)
        second = ProvenanceSource(source_id="test.manual", scope="source", source_version="v1")
        self.assertEqual(_catalog_provenance([second, first], path="/provenance"), (second, first))
        for values, path in (
            ([], "/provenance"),
            ([first, first], "/provenance/1"),
            ([second, second], "/provenance/1"),
            ([ProvenanceSource(source_id="test.manual", scope="source", source_revision=i) for i in range(1, 258)], "/provenance"),
        ):
            with self.subTest(path=path, length=len(values)):
                with self.assertRaises(ContractValidationError) as caught:
                    _catalog_provenance(values, path="/provenance")
                self.assertEqual(caught.exception.path, path)
