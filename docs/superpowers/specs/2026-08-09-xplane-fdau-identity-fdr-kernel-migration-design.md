# xplane-fdau Identity and Native FDR Kernel Migration Design

**Status:** Draft for written-spec review  
**Date:** 2026-08-09  
**Decision owner:** Jeff / tvproductions

## Authority and purpose

The approved cross-project architecture is
`docs/architecture/xplane12_virtual_fdau_ecosystem_design.md`, copied from
q4xpcc commit `04f606dc1a4d25772a679a5afca49ce3257d985d`. It supersedes the
previous decision to release a narrow `xplane-fdr` distribution whose native
X-Plane `.fdr` model was the reusable acquisition boundary.

This specification defines the first independently reviewable transformation
increment. It renames the existing unreleased project and relocates its proven
native X-Plane FDR implementation into the package boundary assigned by the
parent architecture. It does not implement generic FDAU acquisition contracts.
Those contracts require subsequent specifications and plans before the renamed
distribution may be released.

## Project identity

The project identity becomes:

- GitHub repository: `https://github.com/tvproductions/xplane-fdau.git`;
- distribution: `xplane-fdau`;
- import namespace: `xplane_fdau`;
- console command: `xplane-fdau`; and
- expanded name: **Virtual Flight Data Acquisition Unit / Flight Data
  Interface Unit for X-Plane**.

The repository has already been renamed on GitHub. The existing Git history is
authoritative and will be preserved. The local remote will be changed to the
new URL. The linked implementation worktree will be retired only through a
Git-aware sequence after all unique commits are retained on a durable branch.
No repository is recreated, no history is squashed, and the former repository
name is not reused.

The GitHub description is:

> Standard-library-only Python toolkit for acquiring, normalizing, recording,
> replaying, and distributing X-Plane flight data, including native FDR v3/v4
> support.

## Increment goals

This increment will:

1. preserve every accepted native FDR behavior and its regression evidence;
2. rename project, distribution, import, command, documentation, schema URLs,
   workflow, release, and artifact identities coherently;
3. move the native FDR parser, writer, models, profiles, configuration,
   GeoJSON projection, and validation beneath an explicit native-format
   package;
4. move push-first native FDR recording beneath an explicit sink package;
5. make public imports distinguish native FDR samples from future canonical
   FDAU measurement samples;
6. keep all runtime modules standard-library-only, synchronous, capture-neutral,
   and free of host or network imports;
7. fix the existing reader complexity-gate failure while preserving behavior;
8. carry the copied cross-project design and its provenance in this repository;
9. leave a clean base for the next measurement-contract increment; and
10. prevent publication until the canonical vertical slice is complete.

## Non-goals

This increment will not:

- implement `MeasurementDefinition`, `SourceBinding`, raw observations,
  canonical samples, measurement frames, acquisition profiles, demand merging,
  continuity, generic fan-out, canonical archives, manifests, or replay;
- create empty public shells for later FDAU contracts;
- add an XPLM, XPPython3, Web API, q4xpcc, aircraft, or network adapter;
- add ARINC encoders, decoders, tables, constants, or conformance claims;
- implement FDM or FOQA analysis, thresholds, workflow, or legal governance;
- publish to PyPI, create a Git tag or GitHub release, or configure a live
  trusted publisher;
- preserve the unreleased `xplane_fdr` namespace or `xplane-fdr` command as a
  compatibility alias; or
- modify q4xpcc or xpwebapi source code.

## Target package boundary

The increment produces this focused package shape:

```text
xplane_fdau/
|-- __init__.py
|-- formats/
|   |-- __init__.py
|   `-- xplane_fdr/
|       |-- __init__.py
|       |-- errors.py
|       |-- models.py
|       |-- reader.py
|       |-- writer.py
|       |-- profiles.py
|       |-- definition.py
|       |-- config.py
|       |-- geojson.py
|       `-- schemas/
|           `-- fdr-record-config-v1.schema.json
|-- sinks/
|   |-- __init__.py
|   `-- xplane_fdr.py
`-- cli.py
```

`xplane_fdau.__init__` exports only the distribution version during this
increment. It does not flatten native FDR names into the root namespace.
Native-format callers import parsing, modeling, writing, profiles,
configuration, validation errors, and GeoJSON conversion from
`xplane_fdau.formats.xplane_fdr`. Recording callers import
`FDRRecordingSession` and its native recording-definition and destination
helpers from `xplane_fdau.sinks.xplane_fdr`.

`formats.xplane_fdr.definition` owns the immutable native recording,
sampling, and storage definitions consumed by both configuration parsing and
the sink. The sink imports and re-exports those public definition types. This
keeps dependency direction one-way—sink to format—without making callers know
the internal definition module or creating a format-to-sink import cycle.

The split is semantic rather than cosmetic:

- `formats.xplane_fdr` owns the native text format and projections from it;
- `sinks.xplane_fdr` owns publication lifecycle for producing that format;
- neither type is presented as a canonical FDAU measurement or recording; and
- future canonical contracts may depend on neither native format nor sink.

The existing native `FDRSample` remains a positional native-format value. It
is not renamed to a generic sample and is never accepted where a future
`MeasurementSample` is required.

## Native FDR behavior retained

The existing implementation remains the behavioral authority for:

- strict incremental X-Plane FDR v3/v4 reading;
- immutable native header, declaration, sample, and recording models;
- explicit lossy v3-to-canonical-v4 normalization with omission reporting;
- deterministic UTF-8/LF canonical v4 writing;
- push-first and pull-convenience recording into the same sink lifecycle;
- stock native projection profiles and custom DataRef declarations;
- strict adapter-neutral native FDR JSON configuration;
- configurable X-Plane-oriented output storage and deterministic filenames;
- two-dimensional GeoJSON with explicit MSL properties and antimeridian
  splitting;
- offline inspection, validation, and GeoJSON conversion;
- no-replace publication and the approved post-link cleanup contract; and
- standard-library-only runtime and universal-wheel packaging.

Relocation must use history-preserving moves where practical. Behavioral
changes are permitted only when required by the new identity or to make the
existing quality gate pass. Such changes require focused failing tests before
implementation.

## Command-line contract

The console entry point becomes `xplane-fdau`. Native FDR commands are grouped
under an explicit `fdr` namespace:

```text
xplane-fdau fdr inspect INPUT [--json] [--first-utc-date YYYY-MM-DD]
xplane-fdau fdr validate INPUT
xplane-fdau fdr to-geojson INPUT OUTPUT [--overwrite]
```

There is no top-level live-record command. The nested namespace prevents three
native-format utilities from occupying names needed by future canonical
archive, replay, or acquisition tooling. Existing diagnostic, status-code,
stream, strict-JSON, atomic-output, and overwrite behavior remains unchanged.

## Configuration and schema identity

The existing native recording schema remains version 1 and keeps the filename
`fdr-record-config-v1.schema.json`. It moves with the native format package and
continues to describe only native FDR projection and storage choices. Its
`$id`, documentation URL, packaged-resource path, and published copy change to
the `xplane-fdau` identity.

No existing schema consumer has been released, so the old URL is not retained
as a compatibility contract. The schema must not acquire provider connection,
callback, canonical-measurement, ARINC, FOQA, or overwrite settings.

## Documentation migration

The copied ecosystem design becomes the parent architecture and records its
q4xpcc commit and SHA-256 provenance. The former xplane-fdr core design and
implementation plan remain in history and in the repository, but gain an
unambiguous supersession notice linking to the parent architecture and this
increment specification.

README, MkDocs configuration, user guides, API reference, examples, badges,
schema links, repository links, and release instructions will use the new
identity and nested imports. Native FDR documentation will describe the
feature as one deliberately lossy X-Plane replay format and sink. It will not
describe `.fdr` as the canonical FDAU archive.

## Repository and branch migration

The implementation branch currently contains the complete reviewed native FDR
kernel. The migration will preserve it and the earlier design commits. The
implementation plan must begin with read-only branch, worktree, remote, tag,
release, and status checks and record their results.

The safe state transition is:

1. commit this reviewed migration specification on the implementation branch;
2. create and approve a detailed implementation plan;
3. update the shared Git remote to the renamed repository URL;
4. perform package and documentation migration in the existing linked
   worktree;
5. run complete source and installed-artifact verification;
6. integrate the finished branch into `main` without losing commits;
7. remove the linked worktree through `git worktree remove` only after its
   branch is durable and clean;
8. rename the local checkout directory only after linked-worktree metadata no
   longer refers to the former path; and
9. re-run verification from the final checkout path.

No destructive history rewrite, recursive manual worktree deletion, or
unreviewed filesystem rename is allowed.

## External identity checks

Before the increment is declared complete, verification must establish:

- `origin` uses `https://github.com/tvproductions/xplane-fdau.git`;
- project metadata and documentation contain no active old GitHub URL;
- the wheel and sdist are named `xplane_fdau-0.1.0...`;
- installed metadata names the distribution `xplane-fdau` and declares no
  runtime requirements;
- the universal wheel contains `xplane_fdau` and no `xplane_fdr` package;
- the console script is `xplane-fdau` and no `xplane-fdr` alias ships;
- Pages, badges, source links, workflow artifact names, and schema URLs use the
  new identity;
- no release, tag, or publication occurred during migration; and
- q4xpcc and xpwebapi references that require later coordinated edits are
  enumerated for their own plans.

The repository is not a reusable GitHub Action, so GitHub's non-redirect rule
for renamed actions does not require a compatibility repository.

## Error handling and compatibility

The public native FDR exception semantics remain stable under their new module
paths. Parse, validation, configuration, recording-state, and output failures
retain structured source, line, property, and artifact context. Relocation may
not collapse them into generic FDAU errors that do not yet exist.

Because neither `xplane-fdr` nor `xpwebapi.fdr` was publicly released, the new
package provides no import alias, command alias, deprecation shim, or dual
schema publication. Tests must assert absence of those accidental surfaces.

## Verification contract

All tests use `unittest`; pytest is prohibited. The migration is complete only
when fresh evidence shows:

- all relocated behavioral tests pass under the new imports;
- focused import-boundary tests reject `xplane_fdr`, xpwebapi, XPPython3, XPLM,
  q4xpcc, network clients, and third-party runtime imports;
- native FDR fixture, read, write, normalization, recording, configuration,
  GeoJSON, CLI, and publication tests retain their assertions;
- documentation tests enforce the parent architecture, native-projection
  terminology, new URLs, nested CLI, and copied-document provenance;
- Ruff lint and formatting, type checking, coverage, security, documentation,
  dead-code, and Xenon complexity gates all exit zero;
- the existing `_parse_header` Xenon rank-D failure is reduced to the configured
  maximum C or better by a behavior-preserving, test-covered decomposition;
- strict MkDocs builds successfully;
- clean wheel and sdist builds pass strict metadata and archive validation;
- installed-wheel smoke tests pass outside the checkout on Python 3.12, 3.13,
  and 3.14;
- artifact inspection confirms the new names, exact package contents, schema,
  license locations, universal tag, version parity, and empty dependency list;
  and
- the worktree and final checkout are clean with `git diff --check` passing.

## Completion and release boundary

This increment ends with a verified but unreleased `xplane-fdau` distribution
containing the native FDR kernel. It is not the initial public product. Release
remains prohibited until separately reviewed increments implement at least:

1. canonical measurement, binding, observation, sample, frame, timing, and
   quality contracts;
2. acquisition profiles, demand resolution, continuity, and generic fan-out;
3. a rich canonical archive, manifest, recovery behavior, and deterministic
   replay; and
4. an end-to-end projection from canonical samples to the native FDR sink with
   explicit loss reporting.

q4xpcc and xpwebapi integration follows their own reviewed plans after those
contracts exist. ARINC profiles and downstream FDM/FOQA remain later,
independently governed work.
