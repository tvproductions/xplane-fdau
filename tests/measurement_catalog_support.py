"""Synthetic independent catalog vectors; no product catalog content."""

from __future__ import annotations

import hashlib
from typing import Any

from tests.test_measurement_definition_io import ENTRY, PREIMAGE, definition
from xplane_fdau.contracts import Authority, ProvenanceSource
from xplane_fdau.measurements import models

FAMILY = "https://tvproductions.github.io/xplane-fdau/contracts/measurement-catalog"
ENTRY_PREIMAGE = PREIMAGE
DEFINITION_HASH = hashlib.sha256(ENTRY_PREIMAGE).hexdigest()
CATALOG_PREIMAGE = (
    b'{"authority":{"authority_id":"test.authority","authority_revision":1},'
    b'"catalog_id":"test.catalog","catalog_revision":1,'
    b'"contract_family":"https://tvproductions.github.io/xplane-fdau/contracts/measurement-catalog",'
    b'"definitions":[' + ENTRY.rstrip(b"\n") + b"],"
    b'"provenance":[{"scope":"Synthetic","source_id":"test.source","source_revision":1}],'
    b'"schema_version":1}\n'
)
CATALOG_HASH = hashlib.sha256(CATALOG_PREIMAGE).hexdigest()
# Root canonical property order places content_hash immediately before contract_family.
GOLDEN_CATALOG = CATALOG_PREIMAGE.replace(b'"contract_family":', b'"content_hash":"' + CATALOG_HASH.encode() + b'","contract_family":', 1)


def catalog(**changes: Any) -> Any:
    fields: dict[str, Any] = dict(
        contract_family=FAMILY,
        schema_version=1,
        catalog_id="test.catalog",
        catalog_revision=1,
        authority=Authority(authority_id="test.authority", authority_revision=1),
        provenance=[ProvenanceSource(source_id="test.source", scope="Synthetic", source_revision=1)],
        definitions=[definition()],
    )
    return models.MeasurementCatalog(**(fields | changes))
