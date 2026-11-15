"""Independent synthetic binding catalog vectors and model fixtures."""

from __future__ import annotations

import hashlib
import json
from typing import Any

from tests.binding_support import binding as definition
from tests.test_source_binding_definition_io import entry
from xplane_fdau.bindings import models
from xplane_fdau.contracts import Authority, ProvenanceSource

FAMILY = "https://tvproductions.github.io/xplane-fdau/contracts/source-binding-catalog"
ENTRY = json.dumps(entry(), sort_keys=True, separators=(",", ":")).encode() + b"\n"
DEFINITION_HASH = entry()["content_hash"]
CATALOG_PREIMAGE = (
    b'{"authority":{"authority_id":"test.authority","authority_revision":1},'
    b'"catalog_id":"test.catalog","catalog_revision":1,'
    b'"contract_family":"https://tvproductions.github.io/xplane-fdau/contracts/source-binding-catalog",'
    b'"definitions":[' + ENTRY.rstrip(b"\n") + b"],"
    b'"provenance":[{"scope":"Synthetic","source_id":"test.source","source_revision":1}],'
    b'"schema_version":1}\n'
)
CATALOG_HASH = hashlib.sha256(CATALOG_PREIMAGE).hexdigest()
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
    return models.SourceBindingCatalog(**(fields | changes))
