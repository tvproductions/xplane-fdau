# C1.4 Clock Domains, UTC, Anchors, and Simulator Timing Implementation Plan

- **Governance:** active
- **Status:** completed
- **Date:** 2026-10-26
- **Roadmap child:** `C1.4`
- **Source specification:** `docs/superpowers/specs/2026-08-09-xplane-fdau-canonical-measurement-contracts-design.md`
- **Approval:** 2026-10-26 — Jeff / tvproductions; inline execution approved in chat
- **Completion evidence:** `.superpowers/sdd/2026-10-26-c1-4-timing/completion.md`

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deliver the immutable timing contracts and checked clock arithmetic required by C1.4's four acceptance gates.

**Architecture:** `contracts.timing` owns public timing values, vocabularies, arithmetic, and private wire projections. Private timing validation and nested wire readers preserve the existing shape/domain/semantic precedence; explicit canonical dispatch admits the new models without widening the standalone parameter-object API. Simulator I/O and clock sampling remain outside the core.

**Tech Stack:** Python 3.12 standard library; `unittest`, uv, Ruff, ty, strict MkDocs, offline hygiene, and external installed-wheel verification.

**Spec:** [Approved canonical measurement contract design](../specs/2026-08-09-xplane-fdau-canonical-measurement-contracts-design.md), especially “Timing model,” “Public API and errors,” “Timing and lineage tests,” and C1.4 acceptance criteria. The [core-scope amendment](../../architecture/xplane_fdau_core_scope_amendment.md) governs runtime support and adapter ownership.

## Global Constraints

- Implement only `C1.4`. Its dependency `C1.2` is verified. The approved guarded entry transitions selected C1.4 and placed it `in_progress`; delivery gates remain open until their evidence is verified.
- Runtime is pure Python and standard-library-only. Python 3.12 is the sole supported minor. Use the exact execution patch in `.python-version`, currently `3.12.16`, through locked all-group uv commands. Use `unittest` only.
- Public structural models are frozen, slotted, keyword-only dataclasses. Named timing vocabularies are `enum.StrEnum`. Retain the exact public ownership table; add no public model, convenience loader, truncating conversion, or alias beyond the specification.
- `Int64` is `-9223372036854775808..9223372036854775807`; `UInt63` is `0..9223372036854775807`. Reject Boolean/integer/real coercion. Finite binary64 fields require actual floats.
- Optional wire properties are omitted; JSON `null` is prohibited. Use a private omission sentinel, following C1.3's pattern, to distinguish absent fields from supplied nulls. Optional constructor fields default only to that sentinel, never to invented clock, phase, pause, replay, sequence, UTC, or speed values.
- Validate the complete nested shape before canonical domains, then local semantics, following the specification's semantic field order inside each tier. Use RFC 6901 paths, caller source names, and exact parser locations only when available.
- Do not sample clocks, schedule cadence, access a simulator, open recordings, correlate unrelated clocks automatically, extrapolate anchors, synthesize missing timing, or infer one simulator-state field from another.
- Preserve C1.1–C1.3 behavior, root `xplane_fdau.__all__ == ["__version__"]`, and the stdlib runtime boundary. This slice adds no family document, self-hash dispatch, schema, conformance corpus, raw observation, binding catalog, recording, or adapter.
- The supplied `ClockDomain` provides domain identity and units, not a global clock registry. Comparisons do not acquire external context.
- Jeff approved inline execution and local checkpoints on 2026-10-26. This authority applies only to this slice and the separately authorized maintenance baseline; push, tag, publication, and release remain separately gated.

## Review Focus

1. Tick conversion must retain exact rational arithmetic through large intermediate integers; Task 2 tests cancellation, fractional nanoseconds, negative differences, and final-result overflow.
2. UTC conversion must preserve years 0001–9999 and reject sub-microsecond loss on both Windows and POSIX; Task 3 uses numeric date components and tests both precision boundaries.
3. A later nested shape/domain failure must outrank an earlier semantic failure; Task 4 tests competing invalid fields and constructor/reader path parity.
4. Missing timing must remain missing even when other fields suggest a value; Task 4 independently varies pause, replay, source timing, speed, cycle, and simulator time.
5. Public type ownership and installed behavior must survive the new import graph without introducing a contracts-to-bindings dependency; Tasks 4 and 5 test exact exports, import boundaries, and wheel-only behavior.

## Baseline, scope seams, and file map

Observed October 26: `main` at `8bcef360b2728ea4c07b3d41874bc3dd661f051f` has the earlier documentation/Lizard evidence and verified Python dependency refresh as uncommitted changes. Backlog audit and next both report no findings and `action=write_plan child=C1.4`. No child is selected. Preserve those edits; this plan does not assume a clean implementation baseline or absorb the maintenance work into C1.4.

The current session discovers Superpowers 7.0.1 and gz-skills 0.8.0. Native Superpowers version/source metadata and FDAU's older bundle record disagree; the actual 7.0.1 checkout is `2ce8aa15d05bd57213e6f746f953aafb7ded7a8b`. Reconcile the already-open starter provenance work before execution; do not change plugin policy or caches as a C1.4 task.

Execution-source resolution, October 26: entry verified the reviewed 7.0.0 source. During Task 3 the shared cache changed to 7.0.1, and native restoration did not persist. Jeff explicitly approved installed 7.0.1 for the remainder of C1.4. Both observed revisions are now authorized for this run; the execution/TDD/review/verification rules are unchanged. This bounded exception does not update the shared bundle pins or establish starter acceptance.

Two ownership decisions keep the plan within the approved specification:

- `ObservationTiming.acquisition_phase` stores one of the three exact string spellings. `AcquisitionPhase` remains owned by future `bindings.models`; do not export a duplicate enum from `contracts.timing` or create binding models for this slice. The wire contract already specifies the closed strings, while the timing export inventory contains no `AcquisitionPhase`.
- `ObservationTiming` can check its own receipt domain/readings/anchor. Matching its receipt producer to an enclosing record requires that record's producer context, absent from its constructor. Provide a private context check for later C3.1 integration; do not invent a producer field or an unlisted public validation method.

| Responsibility | Files |
| --- | --- |
| Public timing models, enums, arithmetic, and private projections | Create `src/xplane_fdau/contracts/timing.py` |
| Shared phased validation, omission handling, and contextual checks | Create `src/xplane_fdau/contracts/_timing_validation.py` |
| Strict nested wire readers, parser-token preservation, and source/path context | Create `src/xplane_fdau/contracts/_timing_io.py` |
| Explicit canonical dispatch and package exports | Modify `src/xplane_fdau/contracts/canonical_json.py`, `src/xplane_fdau/contracts/__init__.py` |
| Domain/arithmetic/UTC/observation behavior | Create `tests/test_contract_timing.py` |
| Nested parsed-input parity and error precedence | Create `tests/test_contract_timing_io.py`; extend `tests/test_canonical_json.py` |
| Public API and installed module/smoke boundaries | Modify `tests/test_public_api.py`, `tests/test_installed_smoke.py`, `tools/installed_smoke.py`; exercise `tests/test_runtime_import_boundary.py` |
| User guidance and rendered API | Create `docs/reference/contracts-timing.md`; modify `mkdocs.yml`, `tests/test_documentation.py` |
| Execution and delivery evidence | Update this plan after approval; guarded `BACKLOG.md` changes; `.superpowers/sdd/2026-10-26-c1-4-timing/` |

Reuse `_identity_validation` scalar domains and UUID/NFC/counter checks, `_json_parse` token/duplicate/pointer facilities, and the existing C1.3 reader and wire-projection patterns. Keep timing models independent of `canonical_json` to avoid a dispatch/import cycle. Do not refactor unrelated validators or the C1.3 reader.

## Execution entry — after plan approval

- [x] Record approval and the user's execution method. Re-read the approved specification and verify source/plugin authorities, backlog audit/next, HEAD, status, and worktrees. Jeff approved the plan and inline execution on 2026-10-26. Resume verification found no backlog findings; main remains at `8bcef36`. The active sources match the reviewed bundle: Superpowers 7.0.0 at `bb92a77741419a4ab5f06e711a283343f1ada0c3`, gz-skills 0.8.0 at `75bcd11ee9371ecff1a7b3432d2af29d4bdbb788`, and starter at `c0a6945b2170e1cf5bee3e80738916f5b62d13a5`. The earlier 7.0.1 paragraph records a dated observation, not the execution selection. Clean-baseline resolution remains pending; no implementation or lifecycle transition has started.
- [x] Establish a clean reviewed base containing the separately completed maintenance work. Jeff authorized the local checkpoint `a2ef12d`; mandatory hooks passed. No stash or remote operation was used.
- [x] Use `superpowers:using-git-worktrees` at execution time to establish the temporary C1.4 feature worktree. `.worktrees/c1-4-timing`, branch `feature/c1-4-timing`, starts at `a2ef12d` on Python 3.12.16 with locked offline all-group sync.
- [x] After approval, link this plan to C1.4, select C1.4, and transition through `planned` to `in_progress` using each backlog operation's dry-run, target SHA-256, and apply procedure. Each successful mutation audited cleanly; no gate advanced at entry.
- [x] Make the scoped planning/lifecycle commit after authorization. The ledger records combining it with Task 1 in `716f62d`; subsequent task commits run mandatory hooks.

## Public interfaces fixed by this plan

All constructors below are keyword-only. Required fields precede optional fields; an optional field has the private omission sentinel as its default.

| Type | Constructor fields in semantic order |
| --- | --- |
| `ClockDomain` | `clock_domain_id: str`, `kind: ClockKind`, `unit: ClockUnit`, `resolution: int`, `origin: str`, `scope: str`, `producer_instance_id: str`; optional `tick_period: Mapping[str, int]` |
| `ClockReading` | `clock_domain_id: str`, `value: int` |
| `UtcInstant` | `value: str`; its wire value is the string itself, not an object with a `value` property |
| `ClockAnchor` | `monotonic_reading: ClockReading`, `utc: UtcInstant`, `uncertainty_ns: int` |
| `SourceTiming` | `clock: ClockDomain`, `reading: ClockReading`; optional `source_sequence: int` |
| `ObservationTiming` | `receipt_clock: ClockDomain`, `receipt_reading: ClockReading`, `receipt_utc: UtcInstant`; optional `source_timing: SourceTiming`, `receipt_anchor: ClockAnchor`, `xplane_cycle: int`, `simulator_flight_time_ns: int`, `acquisition_phase: str`, `paused: bool`, `replay_state: ReplayState`, `time_speed: float` |

Timing enum members follow the existing uppercase Python member style, with exact wire values: `ClockKind` has `host_monotonic`, `source`, `simulator`; `ClockUnit` has `nanosecond`, `microsecond`, `millisecond`, `tick`; `ReplayState` has `live`, `replay`, `seeking`, `unknown`. Their constructors accept their own enum members or exact string spellings and store the named enum; reject unrelated enum classes and unknown spellings.

`tick_period` is an immutable defensive copy of an exact-property mapping with `numerator_ns` and `denominator`, both positive UInt63 and relatively prime. It is present exactly for `unit == tick`. Do not introduce an unlisted public tick-period class.

Public operations are exactly:

```python
compare_clock_readings(left: ClockReading, right: ClockReading) -> int
difference_clock_readings_ns(later: ClockReading, earlier: ClockReading,
                             domain: ClockDomain) -> int
UtcInstant.to_datetime(self) -> datetime  # aware, timezone.utc; exact conversion only
```

Private projections are `_clock_domain_wire`, `_clock_reading_wire`, `_clock_anchor_wire`, `_source_timing_wire`, and `_observation_timing_wire`, each taking its owned model and returning `dict[str, object]`; `_utc_instant_wire(value: UtcInstant) -> str` returns exact text. They emit optional keys only when present.

After each task's focused GREEN test command, use these exact lint, format,
and type commands (the broader test directory already exists at Task 1):

```powershell
uv run --locked --all-groups ruff check src/xplane_fdau/contracts tests tools/installed_smoke.py
uv run --locked --all-groups ruff format --check src/xplane_fdau/contracts tests tools/installed_smoke.py
uv run --locked --all-groups ty check
```

## Task 1: Clock domains and immutable readings

**Files:** Create `timing.py`, `_timing_validation.py`, and `tests/test_contract_timing.py`; update `tests/test_installed_smoke.py`'s exact module inventory as modules are introduced.

**Interfaces:** Produce `ClockKind`, `ClockUnit`, `ClockDomain`, `ClockReading`, their private projections, and reusable private phased validation. Consume the existing scalar/UUID/NFC checks.

In `tests/test_contract_timing.py`, define `DOMAIN_KWARGS: dict[str, Any]` with the two UUIDs below, `kind="host_monotonic"`, `unit="nanosecond"`, `resolution=1`, `origin="test process origin"`, and `scope="test process"`. The test-only `Any` permits intentional invalid constructor inputs without disabling type diagnostics. Later task examples reuse that fixture. The regression `test_clock_domain_rejects_boolean_resolution` includes:

```python
with self.assertRaises(ContractShapeError) as caught:
    ClockDomain(**(DOMAIN_KWARGS | {"resolution": True}))
self.assertEqual("/resolution", caught.exception.path)
self.assertEqual(1, ClockDomain(**DOMAIN_KWARGS).resolution)
```

- [x] **Step 1 — Write failing behavior tests.** Establish importable declarations, then prove validation/immutability assertions fail before implementation; import errors alone do not complete RED. Test all three clock kinds and four units. For UUIDs use `11111111-1111-4111-8111-111111111111` and producer `22222222-2222-4222-8222-222222222222`. Assert `resolution=1` and `2**63-1` accepted, zero/negative rejected semantically, `True`/`1.0` rejected as shape, and `2**63` rejected as canonical overflow. Test NFC `origin`/`scope` at 1 and 512 characters; reject empty, 513, non-NFC, surrogates, invalid UUIDs, wrong enum spellings, positional construction, mutation, and dynamic attributes.
- [x] **Step 2 — Add tick/readings controls.** Assert tick period `{numerator_ns: 1, denominator: 3}` is preserved, caller mutation cannot affect it, and the stored mapping cannot be mutated. Reject missing/extra keys, `0`, negatives, Booleans, overflow, unreduced `2/6`, absent tick period for ticks, and supplied tick period for other units. Readings preserve both Int64 endpoints and signed values; reject bool, real, string, and overflow without coercion. Check exact error class and JSON Pointer for every representative failure.
- [x] **Step 3 — Verify RED.** Run `uv run --locked --all-groups python -m unittest tests.test_contract_timing tests.test_installed_smoke -v`; retain the assertion failures in the execution directory.
- [x] **Step 4 — Implement the models and validators.** Copy mappings before validation, validate all shapes/domains before semantics, use `math.gcd` for the period, and preserve resolution as metadata rather than multiplying it into readings. Missing optional fields stay absent. Keep helper imports acyclic.
- [x] **Step 5 — Verify GREEN.** Rerun Step 3, then focused `ruff check`, `ruff format --check`, and `ty check` through `uv run --locked --all-groups` on the affected files. Expected: tests pass and no diagnostics.
- [x] **Step 6 — Commit scoped files:** `feat: add immutable clock domains and readings`.

## Task 2: Checked comparison and exact nanosecond differences

**Files:** Extend `timing.py` and `tests/test_contract_timing.py`.

**Interfaces:** Produce the two exact public arithmetic functions above. Consume Task 1's validated models. No clock lookup, sampling, anchoring, or implicit domain conversion is introduced.

The regression `test_tick_difference_is_exact_or_rejected` includes:

```python
domain = ClockDomain(**(DOMAIN_KWARGS | {
    "unit": "tick", "tick_period": {"numerator_ns": 1, "denominator": 3}}))
zero = ClockReading(clock_domain_id=domain.clock_domain_id, value=0)
three = ClockReading(clock_domain_id=domain.clock_domain_id, value=3)
one = ClockReading(clock_domain_id=domain.clock_domain_id, value=1)
self.assertEqual(1, difference_clock_readings_ns(three, zero, domain))
with self.assertRaises(ContractValidationError):
    difference_clock_readings_ns(one, zero, domain)
```

- [x] **Step 1 — Write failing comparisons.** Same-domain readings `1, 2` return `-1`; reversed return `1`; equal readings return `0`. Identical numeric readings from unrelated UUIDs raise `ContractValidationError`. Reject wrong argument model types with `ContractShapeError` before inspecting domain semantics. Comparison does not require a domain object or convert units.
- [x] **Step 2 — Write failing difference assertions.** For values 3 and 1, expect 2 ns, 2000 ns, and 2000000 ns for nanosecond/microsecond/millisecond units. Give microsecond resolution 10 and still expect 2000 ns. Tick period 1/3 with delta 3 yields 1 ns; delta 1 fails as fractional. Negative exact tick differences remain negative. Test supplied domain matching both readings, mismatched domain IDs, zero difference, both final Int64 endpoints, and overflow beyond either endpoint. Include a tick period 1/2 with later `2**63-1` and earlier `-(2**63-1)`: the large intermediate difference is allowed because the final result is exactly `2**63-1` ns.
- [x] **Step 3 — Verify RED** with `uv run --locked --all-groups python -m unittest tests.test_contract_timing -v`; require comparison/arithmetic assertion failures.
- [x] **Step 4 — Implement exact arithmetic.** Use Python integers through subtraction and rational multiplication; require zero remainder before division and enforce Int64 on the final nanosecond result. Unit scales are exactly 1, 1000, and 1000000 ns. Reject fractional conversion instead of rounding. Validate helper arguments in signature order; use `/left`, `/right`, `/later`, `/earlier`, and `/domain` prefixes for argument-local paths, with cross-domain mismatch on the first mismatching later argument's `/clock_domain_id`. Arithmetic-result failures use the root path.
- [x] **Step 5 — Verify GREEN** with Step 3, focused Ruff lint/format, and ty.
- [x] **Step 6 — Commit:** `feat: compare clocks and compute exact nanosecond differences`.

## Task 3: Exact UTC strings and explicit anchors

**Files:** Extend `timing.py`, `_timing_validation.py`, and `tests/test_contract_timing.py`; extend `canonical_json.py` and `tests/test_canonical_json.py` for the types delivered so far.

**Interfaces:** Produce `UtcInstant`, `UtcInstant.to_datetime`, `ClockAnchor`, the UTC/anchor projections, and a private `_validate_clock_anchor(value: ClockAnchor, *, domain: ClockDomain | None = None, path: str = "") -> None` context check. Standalone anchors cannot assert an unavailable domain kind.

The regression `test_utc_preserves_nanoseconds_and_refuses_loss` includes:

```python
instant = UtcInstant(value="2026-10-26T12:34:56.123456789Z")
self.assertEqual(b'"2026-10-26T12:34:56.123456789Z"\n', canonical_bytes(instant))
with self.assertRaises(ContractValidationError):
    instant.to_datetime()
exact = UtcInstant(value="2026-10-26T12:34:56.123456000Z").to_datetime()
self.assertEqual(123456, exact.microsecond)
self.assertEqual(timezone.utc, exact.tzinfo)
```

- [x] **Step 1 — Write failing UTC tests.** `UtcInstant(value="2026-10-26T12:34:56.123456789Z")` retains exactly that text and `canonical_bytes(value)` equals the quoted string plus one LF. Cover year 0001 and 9999, leap day 2000 accepted/1900 rejected, and valid 2024 leap day. Reject missing or 8/10 fractional digits, numeric offsets, lowercase `t`/`z`, leap-second 60, hour 24, invalid dates, whitespace, and non-string inputs. Root UTC errors use the empty pointer because its wire value is a scalar.
- [x] **Step 2 — Write failing conversion/anchor tests.** `.123456000Z` converts to an aware UTC datetime with microsecond 123456; `.123456001Z` raises `ContractValidationError` for precision loss at the UTC root. No truncating method exists. Anchors retain uncertainty 0 and `2**63-1`; reject Boolean/negative/overflow uncertainty. Their readings and UTC survive projection. With a supplied domain, require matching reading UUID and `host_monotonic`; without one, preserve the explicit reading without claiming external correlation.
- [x] **Step 3 — Verify RED** with `uv run --locked --all-groups python -m unittest tests.test_contract_timing tests.test_canonical_json -v`.
- [x] **Step 4 — Implement UTC and anchors.** Full-match the specified ASCII UTC grammar, validate calendar components without platform-dependent `%Y` formatting, retain the original nine digits, and reject nonzero final three digits at datetime conversion. Construct timezone-aware UTC datetimes only on explicit conversion. Add exact-type canonical branches for delivered timing models; a plain string root and arbitrary model/subclass remain unsupported. Never extrapolate an anchor.
- [x] **Step 5 — Verify GREEN** with Step 3, focused Ruff lint/format, and ty. Preserve existing C1.1–C1.3 canonical-byte assertions.
- [x] **Step 6 — Commit:** `feat: preserve nanosecond UTC instants and explicit clock anchors`.

## Task 4: Observation/source timing and strict nested wire parity

**Files:** Extend `timing.py`, `_timing_validation.py`, and `canonical_json.py`; create `_timing_io.py` and `tests/test_contract_timing_io.py`; extend timing/canonical tests and installed-module inventory.

**Interfaces:** Produce `ReplayState`, `SourceTiming`, `ObservationTiming`, remaining projections, and private readers `_clock_domain_from_wire`, `_clock_reading_from_wire`, `_utc_instant_from_wire`, `_clock_anchor_from_wire`, `_source_timing_from_wire`, `_observation_timing_from_wire`. Each reader is `(value: object, *, path: str = "", source: str = "<memory>") -> OwnedModel`, consuming parser-preserved values from `_parse_json_document(data, source=...)`. A private `_validate_observation_producer(value: ObservationTiming, producer_instance_id: str, *, path: str = "") -> None` checks supplied enclosing producer context for later C3.1. These helpers are not public loaders or exports.

The regression `test_minimal_receipt_round_trips_without_invention` includes:

```python
clock = ClockDomain(**DOMAIN_KWARGS)
timing = ObservationTiming(
    receipt_clock=clock,
    receipt_reading=ClockReading(clock_domain_id=clock.clock_domain_id, value=7),
    receipt_utc=UtcInstant(value="2026-10-26T12:34:56.123456789Z"))
wire = canonical_bytes(timing)
loaded = _observation_timing_from_wire(_parse_json_document(wire), source="timing.json")
self.assertEqual(timing, loaded)
self.assertNotIn(b'"paused"', wire)
self.assertNotIn(b'"source_timing"', wire)
```

- [x] **Step 1 — Write failing minimal/full timing tests.** Minimal receipt timing projects exactly `receipt_clock`, `receipt_reading`, and `receipt_utc`; every optional field remains absent. Full timing includes source clock/reading/sequence, receipt anchor, cycle, simulator ns, acquisition phase, pause, replay, and float speed. Round-trip both forms without property invention. Test source clock kinds `source` and `simulator`, reject `host_monotonic`; receipt clock requires `host_monotonic`. Reject reading/domain ID mismatch and receipt anchor reading/UTC mismatch. Context checks accept the matching producer UUID and reject a different supplied producer at `/receipt_clock/producer_instance_id`.
- [x] **Step 2 — Exercise every optional boundary.** Source sequence and cycle use UInt63; simulator time uses Int64. Pause requires an actual bool. Replay accepts exactly its four values; acquisition phase accepts exactly `before_flight_model`, `after_flight_model`, `unknown` as strings. Speed accepts negative, zero, positive, subnormal, and max-finite floats, rejecting int/bool/NaN/infinity. Include `-0.0` and retain C1.1's canonical normalization to `0.0`. Assert each field independently: paused with missing speed does not create speed; replay with no source timestamp creates none; negative replay speed is accepted; absent pause/replay remain absent. Reject explicit null for each optional wire property and supplied constructor null, preserving the corresponding pointer.
- [x] **Step 3 — Write parsed-input and precedence controls.** Parse `canonical_bytes(model)` through the existing parser and private owned reader, then assert model equality, repeated canonical bytes, immutable tick mappings, and all field types. Reject missing/unknown properties, unrelated model inputs, unknown enums, and integer/real token swaps. Test an invalid early clock UUID paired with a later wrong-type pause: shape `/paused` wins; an early semantic resolution zero paired with later Int64 overflow reports the overflow's canonical-domain path first; a nested bad numerator type outranks its invalid denominator value. Programmatic equivalent failures retain the same property pointers where the constructor can represent the same input. Parsed failures retain `source="timing.json"`, and no invented line/column appears on semantic errors. Duplicate properties anywhere fail at the parser stage before either shape or domain errors.
- [x] **Step 4 — Verify RED** with `uv run --locked --all-groups python -m unittest tests.test_contract_timing tests.test_contract_timing_io tests.test_canonical_json tests.test_installed_smoke -v`.
- [x] **Step 5 — Implement the aggregate models and readers.** Traverse the entire selected nested shape, then materialize/check canonical domains, then construct models and apply semantic/context checks in the specified field order. Preserve parsed integer-versus-real tokens until shape validation finishes. Reuse the existing parser; do not add a top-level timing family or public JSON loader. Readers allow a supplied nested pointer and source, and attach it once to errors. Reject unknown properties and explicit null; do not silently drop, sort, coerce, or fill fields.
- [x] **Step 6 — Verify GREEN** with Step 4, focused Ruff lint/format, and ty. Run the existing architecture check as `uv run --locked --all-groups lint-imports`; require zero exit and all declared contracts kept. Keep cognitive UNKNOWN and native Lizard issues separately visible; do not call aggregate analysis a pass.
- [x] **Step 7 — Commit:** `feat: validate and round-trip observation timing evidence`.

## Task 5: Public exports, documentation, installed proof, and gate evidence

**Files:** Modify `contracts/__init__.py`, `tests/test_public_api.py`, `tests/test_installed_smoke.py`, `tools/installed_smoke.py`, `tests/test_documentation.py`, and `mkdocs.yml`; create `docs/reference/contracts-timing.md`; update approved execution progress in this plan and guarded backlog evidence only after verification.

**Interfaces:** `contracts.timing.__all__` is exactly `ClockKind`, `ClockUnit`, `ReplayState`, `ClockDomain`, `ClockReading`, `ClockAnchor`, `UtcInstant`, `ObservationTiming`, `SourceTiming`, `compare_clock_readings`, `difference_clock_readings_ns` in specification row order. Add those delivered names to the contracts package union; add none to the root package. Installed smoke gains private `_canonical_timing_smoke() -> None`.

The regression `test_timing_smoke_detects_incorrect_difference` includes:

```python
with mock.patch.object(contracts, "difference_clock_readings_ns", return_value=99):
    with self.assertRaises(installed_smoke.SmokeError):
        installed_smoke._canonical_timing_smoke()
```

The smoke calls the public contracts namespace, as the existing value smoke does, so this negative control exercises its check rather than an unused patch.

- [x] **Step 1 — Write failing public/installed tests.** Assert the exact timing export inventory and identity of each package re-export; private readers/validators stay private. Add all three new runtime modules to the exact installed module inventory. The installed timing smoke exercises 1/3 tick arithmetic, retained nine-digit UTC, rejected precision loss, matching anchor/receipt timing, minimal optional omission, and unrelated-domain rejection. Add negative controls that prove the smoke fails on altered UTC digits or an incorrect clock difference rather than merely importing names.
- [x] **Step 2 — Verify RED** with `uv run --locked --all-groups python -m unittest tests.test_public_api tests.test_installed_smoke -v`.
- [x] **Step 3 — Complete integration and guidance.** Export the specified names, invoke timing smoke from the installed-smoke entry point, and add a short timing reference page with runnable construction/comparison/UTC examples and MkDocstrings for `xplane_fdau.contracts.timing`. Explain exact UTC conversion, units/resolution, unrelated domains, anchor uncertainty, optional evidence, and adapter ownership. Link it in Reference navigation. Extend documentation verification through existing executable example/API checks, avoiding phrase snapshots.
- [x] **Step 4 — Verify focused GREEN.** Run Step 2 plus `tests.test_documentation` and `tests.test_runtime_import_boundary`; run focused Ruff/format and ty. Build `uv run --locked --all-groups mkdocs build --strict`.
- [x] **Step 5 — Request independent change review** with the approved specification, this plan, four acceptance gates, and actual diff/evidence. Resolve material findings before stable closeout. Review must include arithmetic precision, nested error precedence, exact ownership, unavailable-context limits, and preserved runtime boundaries.
- [x] **Step 6 — Run the stable-candidate full gate once.** New runtime modules change packaged contents, so run `uv run --offline --frozen --all-groups python .codex/skills/hygiene/scripts/hygiene.py`. It supplies all-files Ruff/format/ty/unittest, lock/backlog/docs checks, and a fresh external artifact pair with strict metadata and inventory checks. Do not run a duplicate standalone aggregate on the same candidate. Fix failures and rerun from the first affected gate.
- [x] **Step 7 — Verify the external Python 3.12 wheel.** Use the existing `tools.dependency_matrix.run_matrix(root)` procedure, launched through locked all-group uv, for fresh source/artifact and external installed-wheel checks on the exact `.python-version`. Record command exits, interpreter/import origins, artifact hashes, timing smoke results, and cleanup/preserved-failure paths. Preserve isolation with `--no-project` and the explicit environment interpreter for child commands. This is required for the new installed import surface; no unsupported-minor matrix is added.
- [ ] **Step 8 — Evidence the four gates.** Write each gate receipt with exact candidate identity, commands/results and bounded review findings. Use the guarded backlog adapter's dry-run/target-hash/apply procedure to record gates and advance only C1.4 after all requirements pass. A routine suite does not certify deferred starter STRICT acceptance, G1, or release readiness.
- [ ] **Step 9 — Commit:** `feat: expose and verify canonical timing contracts`; keep independent review and gate-recording changes scoped. Do not bypass hooks. Any later code correction invalidates its affected earlier gate evidence.
- [ ] **Step 10 — Finish through the selected integration route.** After branch verification, use `superpowers:finishing-a-development-branch`. If Jeff selects local integration, follow AGENTS.md's exact fast-forward verification; retain branch/worktree until main verification passes. Push/tag/publication remain separately authorized.

## Acceptance traceability

| Backlog gate | Implementation and tests | Required evidence |
| --- | --- | --- |
| 1. Domains/readings preserve unit, resolution, origin, scope, producer | Task 1, Task 4 reader parity; frozen/defensive-copy controls | Focused model/reader tests; canonical projection and installed smoke |
| 2. UTC preserves exact nanoseconds and `Z` | Task 3, Task 4 nested UTC; date/precision negatives | Exact canonical bytes, round trips, no-loss conversion rejection, installed smoke |
| 3. Same-domain comparison; unrelated domains fail | Task 2; Task 5 incorrect-result negative control | Signed comparison, rational/exact difference, fractional/overflow rejection |
| 4. Anchors, uncertainty, source/simulator timing and optional states round-trip without invention | Tasks 3–4; Task 5 full/minimal installed examples | Nested parity/precedence, equality/absence assertions, context-check limits, independent review |

## Drafting self-review and plan audit

Intent is the approved canonical design; scope is C1.4's four backlog gates. Planning verification is distinct from execution acceptance.

| Intent to scope | Assessment |
| --- | --- |
| Typed clock metadata and distinct timing domains → gate 1 | Aligned: spec “Timing model”; Task 1 |
| Exact UTC text and precision-safe conversion → gate 2 | Aligned: spec UTC paragraphs; Task 3 |
| Checked related-clock arithmetic → gate 3 | Aligned: spec timing/public signatures; Task 2 |
| Explicit observed timing, anchors and states → gate 4 | Aligned: spec ObservationTiming inventory; Tasks 3–4 |
| Transport independence, no fabricated evidence, exact public ownership | Aligned: global constraints and scope-seam decisions |

| Scope to plan | Assessment |
| --- | --- |
| Every C1.4 gate has implementation, negative controls, and installed proof | Aligned: acceptance traceability above |
| Existing C1.1–C1.3 validators/parser remain authoritative | Aligned: file map and Tasks 1, 3–4 |
| Parent-record producer matching requires external context | Aligned: private context check now; actual RawObservation integration belongs to C3.1 |
| No unlisted AcquisitionPhase export or contracts-to-bindings dependency | Aligned: phase remains the specified closed wire string in this slice |
| Source/resource delivery and verification boundaries | Aligned: Task 5 hygiene, wheel verification, review and controlled gate evidence |
| Selection, approval, execution and remote/release authority | Aligned: draft metadata and execution-entry conditions |

Drafting self-review checked field names/signatures, semantic order, arithmetic units and bounds, exact export ownership, nullable/omitted distinction, and mapping of all five Review Focus cases. Its earlier audit and logs remain drafting evidence. Jeff subsequently approved execution; delivery acceptance requires the separate execution review and gate receipts.
