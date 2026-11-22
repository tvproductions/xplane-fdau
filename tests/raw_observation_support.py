"""Synthetic raw-observation vectors independent of runtime serialization."""

from __future__ import annotations

import json
from hashlib import sha256

FAMILY = "https://tvproductions.github.io/xplane-fdau/contracts/raw-observation"
SCHEMA_NAME = "raw-observation-v1.schema.json"
SCHEMA_ID = "https://tvproductions.github.io/xplane-fdau/schemas/" + SCHEMA_NAME
CONTENT_HASH = "64903f6b6d62750e6fb562eacb240b1efef76336f0b4ca44f41b1f3ab5941f83"
DOCUMENT_HASH = "03b6b3039898418347fc681448134333fdc5a7900650bbeea5ab5f11bb879c03"


def uid(number: int) -> str:
    return f"00000000-0000-4000-8000-{number:012d}"


def independent_bytes(document: dict[str, object]) -> bytes:
    """Encode the simple ASCII vector, whose scalars need no binary64 handling."""
    return (json.dumps(document, sort_keys=True, separators=(",", ":")) + "\n").encode("ascii")


def raw_observation_wire() -> dict[str, object]:
    """Build a fresh receipt-only fixture with independent canonical identity."""
    document: dict[str, object] = {
        "contract_family": FAMILY,
        "schema_version": 1,
        "observation_id": uid(1),
        "producer": {"implementation_id": "test.producer", "implementation_version": "1", "producer_instance_id": uid(2)},
        "provider": {"provider_family_id": "test.provider", "provider_version": "1"},
        "adapter": {"adapter_family_id": "test.adapter", "adapter_version": "1"},
        "session_id": uid(3),
        "stream_id": uid(4),
        "epoch_id": uid(5),
        "sequence": 0,
        "connection_generation": 0,
        "source_generation": 0,
        "resource_kind": "test.resource",
        "resource_id": "test/source",
        "observed_shape": [],
        "observed_representation": "boolean",
        "value_evidence": {"kind": "inline", "value": {"representation": "boolean", "value": False}},
        "timing": {
            "receipt_clock": {
                "clock_domain_id": uid(6),
                "kind": "host_monotonic",
                "unit": "nanosecond",
                "resolution": 1,
                "origin": "test",
                "scope": "test",
                "producer_instance_id": uid(2),
            },
            "receipt_reading": {"clock_domain_id": uid(6), "value": 0},
            "receipt_utc": "2026-11-22T00:00:00.123456789Z",
        },
        "applicability_context": [],
        "status": "ok",
        "limitations": [],
    }
    document["content_hash"] = sha256(independent_bytes(document)).hexdigest()
    return document
