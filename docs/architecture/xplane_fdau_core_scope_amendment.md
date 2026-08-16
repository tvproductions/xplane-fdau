# X-Plane FDAU core scope amendment

**Status:** Approved
**Date:** 2026-08-16
**Approval:** 2026-08-16 — Jeff / tvproductions
**Scope:** `xplane-fdau` purpose, ownership, adapter boundaries, standards,
FDM/FOQA, and Python compatibility

## Authority

This repository preserves the imported
[`xplane12_virtual_fdau_ecosystem_design.md`](xplane12_virtual_fdau_ecosystem_design.md)
byte-for-byte for provenance. This amendment records the later architectural
clarifications approved for `xplane-fdau`. Where the imported design places
FDM/FOQA in a separate downstream project or can be read as making the core
simulator-neutral, this amendment supersedes that guidance.

The imported design remains authoritative for canonical identity, timing,
quality, continuity, artifact, regulatory, conformance, and adapter-isolation
requirements that this amendment does not change.

## Decision

`xplane-fdau` is the transport-free, standard-library-only flight-data kernel for
X-Plane. It defines and processes X-Plane flight-data semantics and artifacts,
while external XPPython3/XPLM and `xplane-webapi` clients perform all simulator
I/O through its ports. It is not a simulator-neutral avionics platform and it
does not communicate with X-Plane itself.

The governing topology is:

```text
X-Plane <-> external client/adapter <-> xplane-fdau ports <-> core behavior
```

Both directions across the X-Plane boundary belong to external clients. An
adapter may acquire observations from X-Plane, submit them through an FDAU
input port, consume frames or findings through an output port, and then write
back or publish elsewhere. None of those transport operations move into this
distribution.

## X-Plane bounded context

Transport independence does not mean domain independence. The core exists to
support an ecosystem whose source, semantics, recordings, replay, and analysis
are tied to X-Plane. Its provider-neutral contracts are neutral among X-Plane
access paths and recorded evidence:

- an XPPython3/XPLM plugin client running inside X-Plane;
- an external client using `xplane-webapi`;
- native X-Plane FDR files;
- canonical FDAU archives and deterministic replay; and
- fixtures or test adapters that model those same contracts.

General real-aircraft acquisition, arbitrary simulator support, and a generic
avionics integration platform are outside this project's purpose. A future
non-X-Plane product would require a separate design decision rather than
quietly broadening these contracts.

## Ports and external clients

The core owns host-neutral ports, domain values, deterministic transformations,
and artifacts. External clients own every concrete mechanism that reaches into
or out of X-Plane, including:

- XPLM handles, DataRef lookup, callbacks, and plugin lifecycle;
- XPPython3 entry points and embedded-interpreter packaging;
- REST, WebSocket, UDP, sockets, authentication, and connection management;
- simulator discovery, aircraft loading, process control, and scheduling; and
- provider-specific resource catalogs and error recovery.

`q4xpcc` and clients built on `xplane-webapi` may depend on `xplane-fdau`.
`xplane-fdau` must never import or acquire a runtime dependency on q4xpcc,
`xplane-webapi`, XPPython3, `xp`, XPLM, or a network client. No provider SDK or
host object may cross a core port.

The adapter is therefore a client of the application/core ports, even when it
performs both ingress and egress. Calling these projects clients is important:
it preserves dependency inversion and prevents transport details from becoming
the core's organizing model.

## Core ownership

This distribution is the home for reusable X-Plane flight-data behavior:

1. canonical measurement identity, binding, units, observations, timing,
   quality, lineage, continuity, acquisition, and fan-out;
2. canonical archive writing, recovery, inspection, and deterministic replay;
3. native X-Plane FDR parsing, projection, writing, and recording sinks;
4. edition-pinned ARINC profiles, codecs, mappings, validation, and
   conformance fixtures; and
5. X-Plane flight-data monitoring and FOQA-oriented analysis over canonical
   evidence, including event detection, derived values, segmentation, and
   analysis findings.

These capabilities should remain cohesive but modular within one pure-Python,
standard-library-only distribution. Separate packages or distributions require
a demonstrated lifecycle or dependency need and a reviewed architecture
change; they are not the default decomposition.

The dependency direction stays inward. FDR projections, ARINC representations,
and analysis consume canonical contracts. Acquisition and canonical recording
must not depend on a particular file projection, standard profile, event rule,
or FOQA program policy.

## Native FDR and ARINC are distinct formats

Native X-Plane textual `.fdr` v3/v4 is a deliberately lossy X-Plane replay
projection and sink. It is not an ARINC flight-recorder or QAR format and it is
not the canonical archive.

ARINC implementations are nevertheless first-class core work because shared,
Python-native standards behavior benefits every X-Plane client. The standards
layer may provide standard-library-only data models, encoders, decoders,
profiles, mappings, validators, and deterministic conformance corpora. Concrete
bus access, network transport, device integration, and simulator I/O remain
external adapter responsibilities.

ARINC work must be edition-pinned, requirements-traced, and based on licensed
normative material where required. A profile must state what it implements and
must not imply conformance to an entire ARINC family. Canonical measurement
identity remains primary:

```text
X-Plane source binding
    -> canonical measurement and observation
    -> edition-pinned ARINC mapping/profile
    -> ARINC representation
```

This separation lets q4xpcc, `xplane-webapi` clients, offline tools, and tests
share identical standards behavior without duplicating or embedding it in a
provider adapter.

## FDM and FOQA are required core capabilities

X-Plane flight-data monitoring and FOQA-oriented analysis belong in
`xplane-fdau`, not in a future generic downstream library and not solely in
consumer applications. This is a firm product responsibility, although its
implementation follows the canonical acquisition, recording, and replay
foundation in the roadmap. FDM/FOQA consumes the same canonical evidence
whether observations arrived through an XPPython3 client, a `xplane-webapi`
client, native FDR import, or archive replay.

Within this architecture, **flight data monitoring (FDM)** is the reusable
technical capability: validate recorded evidence, derive parameters, segment
flights and phases, detect and classify events, support event validation,
aggregate results, analyze trends, and produce reviewable findings. **FOQA** is
the safety-program context in which an authorized organization may configure,
review, govern, protect, and act on those technical results. `xplane-fdau`
owns the former and provides explicit ports and records needed by the latter;
it does not impersonate the organization that operates a FOQA program.

The required local analysis pipeline is:

```text
canonical evidence
    -> evidence qualification
    -> flight/phase segmentation and derived parameters
    -> versioned event-set evaluation
    -> candidate findings
    -> event validation/review state
    -> aggregation, trends, and report projections
```

The same deterministic input, analysis profile, and library version must
produce the same technical result. Each result must preserve enough provenance
to identify the evidence, parameter definitions, derived-value algorithms,
event definition and severity rules, analysis profile, and software version.
Profile changes must not silently rewrite historical meaning; cross-version
aggregation must either normalize explicitly or preserve the version boundary.

Acquisition quality and operational findings are different concepts:

- acquisition quality describes whether evidence is missing, stale,
  discontinuous, converted, degraded, or otherwise unsuitable; and
- an operational finding is an analysis result produced from qualified
  evidence under a versioned rule or program profile.

Analysis must preserve that distinction, reject or qualify inadequate evidence,
and retain rule/profile identity and provenance. The library may implement
FOQA-oriented mechanics and X-Plane analysis profiles, but it must not claim
that installing or running the library creates an FAA-approved FOQA program,
Part 193 protection, regulatory custody, or an operator's governance process.
Those claims require external organizational authority.

### FAA AC 120-82 design input

[FAA Advisory Circular 120-82, *Flight Operational Quality Assurance*](https://www.faa.gov/documentLibrary/media/Advisory_Circular/AC_120-82.pdf)
is an explicit design source for the FDM/FOQA bounded context. It describes one
acceptable means of establishing and operating a voluntary air-carrier FOQA
program; it is guidance, not a certification conferred on this X-Plane
library. Its software and data-flow concepts inform the core as follows:

| AC 120-82 concept | `xplane-fdau` responsibility | External responsibility |
| --- | --- | --- |
| Airborne collection and recorded parameters | Canonical measurement, timing, quality, recording, recovery, and replay contracts | X-Plane transport, parameter discovery, and acquisition client |
| Ground data replay and analysis | Deterministic transformation, scanning, derived values, event algorithms, and report projections | Hosting, scheduling, user interface, and distribution |
| Data validation | Evidence qualification, reasonableness/consistency checks, invalid-evidence disposition, and retained quality provenance | Corroborating sources and authorized operational judgment |
| Events, levels, sets, and routine operational measurements | Versioned profile models, parameter prerequisites, phase/context rules, severity classification, and conformance tests | Organization- and aircraft-specific approved limits and source authority |
| Event validation | Candidate-versus-validated finding states, review evidence, and auditable decision records | Authorized reviewer, investigation, crew contact, and final operational determination |
| Aggregate data and trend analysis | Reproducible grouping, statistics, comparable-profile checks, and report-ready projections | Risk interpretation, stakeholder review, and corrective-action decisions |
| De-identification, access, retention, and security | Policy ports, classification metadata, transformations that can be tested, and safe defaults where specified | Identity custody, authorization, storage security, retention policy, and legal compliance |
| Corrective action and follow-up | Stable finding references and feedback/status records that applications can persist or exchange | Decision authority, implementation, monitoring, and program governance |

This mapping makes several design constraints mandatory:

- analysis never treats an unqualified or incomplete parameter stream as
  silently valid;
- event definitions declare required measurements, units, sampling/continuity
  assumptions, derived parameters, applicable aircraft/profile context,
  severity levels, and source provenance;
- candidate detection and event validation are separate states because a
  threshold crossing alone does not prove a valid operational event;
- aggregation and trend analysis preserve event-definition versions and reject
  misleading comparisons;
- de-identification is an explicit transformation with traceable policy, not
  an undocumented field deletion;
- reports are projections from preserved evidence and findings, not the system
  of record; and
- the public API uses conditional language such as `FOQA-oriented` unless an
  external approved program supplies the applicable governance.

The FAA circular also reinforces why FDM/FOQA must live beside the FDAU
contracts: available parameters, sample rates, recording accuracy, continuity,
and data validity directly constrain what analysis can support. Keeping these
concerns in one dependency-directed core lets findings carry acquisition truth
instead of reconstructing or guessing it in each client.

## Python compatibility policy

An exact project-wide Python `3.12.x` pin would unnecessarily constrain the
transport-free core and external `xplane-webapi` compositions. The core instead
uses a compatibility floor and a tested version range:

- Python 3.12 is the minimum compatibility floor and the syntax/API discipline
  for code that may be composed into an XPPython3 client;
- Python 3.12 is a mandatory source and installed-wheel verification target;
- Python 3.13 and 3.14 are also source and installed-wheel verification targets;
  and
- support for a later minor version is added deliberately through a reviewed
  metadata, CI, lockfile, and installed-artifact update.

Until that next compatibility review, distribution metadata should express
`>=3.12,<3.15`. The upper bound marks the end of the verified range; it is not
an assertion that later Python versions are intrinsically incompatible.

The distribution must not require every consumer to run the same interpreter.
Code imported into an XPPython3 process necessarily runs on, and must be
compatible with, that process's embedded interpreter. An external
`xplane-webapi` client may use any Python version supported by both projects.
The concrete XPPython3 client owns any exact interpreter pin needed for its
deployable plugin artifact.

This compatibility policy is separate from pinning the repository's `uv` CLI
version for reproducible maintenance. The `uv` pin should be refreshed toward
new stable releases through the governed dependency-refresh workflow rather
than allowed to become permanent infrastructure drift.

## Roadmap consequences

The canonical vertical-slice release gate remains unchanged. This amendment
does not pull ARINC or FOQA implementation into the first release gate.

The roadmap and backlog implement this decision as follows:

- retain the local standards epics and make their shared-client purpose
  explicit;
- replace the former separate-downstream FDM/FOQA ownership entries with local,
  dependency-ordered analysis epics;
- retain external organizational governance as a boundary on regulatory and
  program claims, not as ownership of the reusable analysis code;
- keep q4xpcc and `xplane-webapi` integrations as external client/adapter work;
- record the multi-version Python compatibility and installed-wheel gates; and
- add the approved dependency-refresh skill parity work without comparing or
  vendoring the external Superpowers checkout.

## Acceptance criteria

This clarification is reflected consistently when:

- public documentation calls `xplane-fdau` an X-Plane-specific,
  transport-free kernel;
- no documentation implies that this project connects to X-Plane;
- XPPython3/XPLM and `xplane-webapi` implementations remain external clients
  of core ports;
- native FDR, canonical FDAU, and ARINC representations remain distinct;
- ARINC codecs and profiles are core-owned, standard-library-only,
  edition-pinned capabilities;
- X-Plane FDM/FOQA mechanics are core-owned while regulatory governance and
  claims remain external;
- Python 3.12 compatibility is mandatory without imposing an exact 3.12.x pin
  on every composition; and
- roadmap, backlog, package boundaries, and verification gates follow these
  decisions before the affected capabilities are implemented.
