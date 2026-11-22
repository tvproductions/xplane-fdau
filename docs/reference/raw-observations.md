# Raw observations

A [version-1 raw observation](../schemas/raw-observation-v1.schema.json)
records the value and metadata an adapter gathered from one source. The
record preserves provider, adapter, resource, generation, observed
representation, and shape. The binding describes the expected source
separately. This API can carry an inline typed value, a content-addressed
payload reference, or an explicit absence.

For an unavailable value, supply the observed type and shape if the adapter
has them for that source generation. For example, a failed read of a known
scalar Boolean can carry an absent value with a known Boolean representation.
A failure before the source metadata is known lacks the required record
fields. Supply receipt clock and UTC evidence explicitly. Source timing is
an optional independent field for genuinely supplied source-clock evidence.

## Record a received Boolean

The example uses synthetic identifiers and a known scalar shape. An empty
limitations sequence serializes as an empty array. The canonical byte and
binary-stream functions emit UTF-8 with one final LF. A caller-owned binary
stream stays open after either operation.

```python
from dataclasses import replace
from io import BytesIO

from xplane_fdau.acquisition import (
    RawObservation,
    RawValueEvidence,
    dump_raw_observation_v1,
    dumps_raw_observation_v1,
    load_raw_observation_v1,
)
from xplane_fdau.contracts import (
    AdapterIdentity,
    ClockDomain,
    ClockReading,
    InlineValue,
    ObservationTiming,
    ProducerIdentity,
    ProviderIdentity,
    UtcInstant,
)

producer = ProducerIdentity(
    implementation_id="test.adapter",
    implementation_version="1",
    producer_instance_id="00000000-0000-4000-8000-000000000001",
)
receipt_clock = ClockDomain(
    clock_domain_id="00000000-0000-4000-8000-000000000002",
    kind="host_monotonic",
    unit="nanosecond",
    resolution=1,
    origin="monotonic receipt clock",
    scope="adapter process",
    producer_instance_id=producer.producer_instance_id,
)
observation = RawObservation(
    contract_family="https://tvproductions.github.io/xplane-fdau/contracts/raw-observation",
    schema_version=1,
    observation_id="00000000-0000-4000-8000-000000000003",
    producer=producer,
    provider=ProviderIdentity(provider_family_id="test.provider", provider_version="1"),
    adapter=AdapterIdentity(adapter_family_id="test.adapter", adapter_version="1"),
    session_id="00000000-0000-4000-8000-000000000004",
    stream_id="00000000-0000-4000-8000-000000000005",
    epoch_id="00000000-0000-4000-8000-000000000006",
    sequence=0,
    connection_generation=0,
    source_generation=0,
    resource_kind="test.resource",
    resource_id="test/source",
    observed_shape=(),
    observed_representation="boolean",
    value_evidence=RawValueEvidence(
        kind="inline", value=InlineValue(representation="boolean", value=False)
    ),
    timing=ObservationTiming(
        receipt_clock=receipt_clock,
        receipt_reading=ClockReading(clock_domain_id=receipt_clock.clock_domain_id, value=95),
        receipt_utc=UtcInstant(value="2026-11-22T00:00:00.123456789Z"),
    ),
    applicability_context=(),
    status="ok",
    limitations=(),
)

wire = dumps_raw_observation_v1(observation)
with BytesIO() as stream:
    dump_raw_observation_v1(observation, stream)
    stream.seek(0)
    restored = load_raw_observation_v1(stream, source="example")

unavailable = replace(
    observation,
    observation_id="00000000-0000-4000-8000-000000000007",
    sequence=1,
    status="unavailable",
    value_evidence=RawValueEvidence(kind="absent", reason="unavailable"),
)
```

The first record contains a received Boolean false. The second represents an
unavailable read with the same known source metadata. A payload reference
carries a claimed byte length, digest, media type, role and retention status.
The caller owns payload retrieval and storage.
