# Canonical timing contracts

Timing records evidence supplied by an external adapter. These contracts do
not sample clocks, schedule acquisition, contact X-Plane, or manufacture source
timestamps. Simulator I/O and host lifecycle remain adapter responsibilities.

## Domains, units, and anchors

Each `ClockDomain` identifies its producer, origin, scope, integer unit, and
advertised resolution. Resolution is metadata: it does not scale readings.
Comparison requires matching domain IDs. Differences use the supplied domain
and return exact signed integer nanoseconds; unrelated domains, fractional
nanoseconds, and final Int64 overflow raise `ContractValidationError`.

```python
from xplane_fdau.contracts import (
    ClockAnchor, ClockDomain, ClockReading, ObservationTiming, UtcInstant,
    canonical_bytes, difference_clock_readings_ns,
)

clock = ClockDomain(
    clock_domain_id="11111111-1111-4111-8111-111111111111",
    kind="host_monotonic", unit="microsecond", resolution=10,
    origin="process monotonic clock", scope="capture process",
    producer_instance_id="22222222-2222-4222-8222-222222222222",
)
earlier = ClockReading(clock_domain_id=clock.clock_domain_id, value=1)
later = ClockReading(clock_domain_id=clock.clock_domain_id, value=3)
elapsed_ns = difference_clock_readings_ns(later, earlier, clock)
assert elapsed_ns == 2000

utc = UtcInstant(value="2026-10-26T12:34:56.123456789Z")
anchor = ClockAnchor(monotonic_reading=later, utc=utc, uncertainty_ns=500)
receipt = ObservationTiming(
    receipt_clock=clock, receipt_reading=later, receipt_utc=utc,
    receipt_anchor=anchor,
)
wire = canonical_bytes(receipt)
```

For tick units, supply a positive reduced rational `tick_period`, such as
`{"numerator_ns": 1, "denominator": 3}`. A difference of three ticks then
represents one nanosecond; one tick cannot be rounded to an integer nanosecond.

An anchor correlates UTC with its exact monotonic reading and retains the
stated uncertainty. It provides no extrapolation, rate, drift correction, or
automatic correlation between unrelated clock domains. A receipt anchor must
match its enclosing receipt's domain, reading, and UTC text.

## Exact UTC and optional evidence

`UtcInstant` preserves exactly nine fractional digits and uppercase `Z`, with a
valid Gregorian date from year 0001 through 9999. Offsets, leap-second `60`, and
alternate spellings are rejected. Python datetime conversion succeeds only when
the final three fractional digits are zero; it returns an aware UTC datetime.

```python
from xplane_fdau.contracts import ContractValidationError

precision_rejected = False
try:
    utc.to_datetime()
except ContractValidationError:
    precision_rejected = True
assert precision_rejected

exact_datetime = UtcInstant(value="2026-10-26T12:34:56.123456000Z").to_datetime()
assert exact_datetime.microsecond == 123456
```

`SourceTiming` carries a source or simulator domain, its matching reading, and
an optional source sequence. `ObservationTiming` requires host-monotonic receipt
timing and UTC. Source timing, anchors, cycle, simulator flight time, acquisition
phase, pause, replay state, and time speed are independently optional. Omit
unavailable fields; explicit null is prohibited. A paused state does not imply
a speed, and replay does not supply a missing source timestamp. Negative, zero,
and positive finite speed factors remain representable.

The contracts package exports the timing models and checked operations. These
nested values have canonical serialization; family-document loaders and schemas
belong to later contract slices.

::: xplane_fdau.contracts.timing
    options:
      show_source: false
      members_order: source
