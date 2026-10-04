"""C1.2 canonical self-hash preimage vectors."""

from __future__ import annotations

from copy import deepcopy
import unittest

from xplane_fdau.contracts._content_hash import (
    _definition_content_hash,
    _definition_preimage,
    _record_content_hash,
    _record_preimage,
)
from xplane_fdau.contracts.errors import ContractValidationError


FAMILY = "https://tvproductions.github.io/xplane-fdau/contracts/measurement-catalog"
RECORD_PREIMAGE = (
    b'{"nested":{"content_hash":"bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"},'
    b'"record_id":"12345678-1234-1234-8234-123456789abc","value":1.0}\n'
)
RECORD_DIGEST = "d1bcf9869ac210446527b4ce344db5256a0420a70a4bcc432d73023ac0c9fa3e"
DEFINITION_PREIMAGE = (
    b'{"contract_family":"https://tvproductions.github.io/xplane-fdau/contracts/measurement-catalog",'
    b'"definition":{"authority":{"authority_id":"test.owner","authority_revision":1},'
    b'"definition_id":"test.altitude","definition_revision":2,"provenance":'
    b'[{"scope":"manual","source_id":"test.manual","source_revision":1}],'
    b'"quantity_id":"test.pressure_altitude"},"schema_version":1}\n'
)
DEFINITION_DIGEST = "4645ff5b3d74719279bd5492047f14355361214f13d8f4ec794ed5145d5f97dd"


class ContentHashTests(unittest.TestCase):
    def record(self) -> dict[str, object]:
        return {
            "content_hash": "a" * 64,
            "nested": {"content_hash": "b" * 64},
            "record_id": "12345678-1234-1234-8234-123456789abc",
            "value": 1.0,
        }

    def definition(self) -> dict[str, object]:
        return {
            "content_hash": "a" * 64,
            "authority": {"authority_id": "test.owner", "authority_revision": 1},
            "definition_id": "test.altitude",
            "definition_revision": 2,
            "provenance": [{"scope": "manual", "source_id": "test.manual", "source_revision": 1}],
            "quantity_id": "test.pressure_altitude",
        }

    def test_record_preimage_omits_only_root_hash_and_keeps_nested_hash(self) -> None:
        record = self.record()
        original = deepcopy(record)
        self.assertEqual(_record_preimage(record), RECORD_PREIMAGE)
        self.assertEqual(_record_content_hash(record), RECORD_DIGEST)
        self.assertEqual(record, original)
        record.pop("content_hash")
        self.assertEqual(_record_content_hash(record), RECORD_DIGEST)
        reordered = {key: record[key] for key in reversed(record)}
        self.assertEqual(_record_content_hash(reordered), RECORD_DIGEST)
        changed = deepcopy(record)
        changed["nested"] = {"content_hash": "c" * 64}
        self.assertNotEqual(_record_content_hash(changed), RECORD_DIGEST)
        changed = deepcopy(record)
        changed["record_id"] = "22345678-1234-1234-8234-123456789abc"
        self.assertNotEqual(_record_content_hash(changed), RECORD_DIGEST)

    def test_definition_preimage_pins_family_revision_authority_provenance_and_body(self) -> None:
        definition = self.definition()
        original = deepcopy(definition)
        self.assertEqual(_definition_preimage(FAMILY, definition), DEFINITION_PREIMAGE)
        self.assertEqual(_definition_content_hash(FAMILY, definition), DEFINITION_DIGEST)
        self.assertEqual(definition, original)
        definition.pop("content_hash")
        self.assertEqual(_definition_content_hash(FAMILY, definition), DEFINITION_DIGEST)
        reordered = {key: definition[key] for key in reversed(definition)}
        self.assertEqual(_definition_content_hash(FAMILY, reordered), DEFINITION_DIGEST)
        for key, value in (
            ("definition_id", "test.airspeed"),
            ("definition_revision", 3),
            ("authority", {"authority_id": "test.other", "authority_revision": 1}),
            ("provenance", [{"scope": "other", "source_id": "test.manual", "source_revision": 1}]),
            ("quantity_id", "test.geometric_altitude"),
        ):
            with self.subTest(key=key):
                changed = deepcopy(definition)
                changed[key] = value
                self.assertNotEqual(_definition_content_hash(FAMILY, changed), DEFINITION_DIGEST)
        self.assertNotEqual(
            _definition_content_hash("https://tvproductions.github.io/xplane-fdau/contracts/source-binding-catalog", definition),
            DEFINITION_DIGEST,
        )

    def test_rejects_bad_self_hash_and_unsupported_definition_family(self) -> None:
        record = self.record()
        record["content_hash"] = "A" * 64
        with self.assertRaises(ContractValidationError) as caught:
            _record_content_hash(record)
        self.assertEqual(caught.exception.path, "/content_hash")
        definition = self.definition()
        definition["content_hash"] = "A" * 64
        with self.assertRaises(ContractValidationError) as caught:
            _definition_content_hash(FAMILY, definition)
        self.assertEqual(caught.exception.path, "/definition/content_hash")
        with self.assertRaises(ContractValidationError) as caught:
            _definition_content_hash("https://tvproductions.github.io/xplane-fdau/contracts/raw-observation", self.definition())
        self.assertEqual(caught.exception.path, "/contract_family")
