# xplane-fdr Core Design

> **Superseded 2026-08-09:** The approved project identity and architecture are
> now the virtual FDAU/FDIU ecosystem described in
> `docs/architecture/xplane12_virtual_fdau_ecosystem_design.md`. The native FDR
> implementation remains retained migration material under
> `docs/superpowers/specs/2026-08-09-xplane-fdau-identity-fdr-kernel-migration-design.md`.
> This document is historical and must not drive new implementation.

## Purpose

Create `xplane-fdr` as the reusable, capture-neutral implementation of the
X-Plane Flight Data Recorder domain. The project reads, validates, writes,
records, and converts native X-Plane FDR data without depending on a network
client, an in-simulator plugin host, or any third-party Python package.

The repository is `tvproductions/xplane-fdr`, the PyPI distribution is
`xplane-fdr`, and the import package is `xplane_fdr`.

The project description is:

> A standard-library-only Python toolkit for reading, writing, recording,
> validating, and converting X-Plane Flight Data Recorder files, independent
> of how flight data is captured.

## Architectural Decision

The FDR domain will not be owned by `xpwebapi`. It has at least two concrete
capture environments with different dependency and execution constraints:

- `xpwebapi` receives values from an external Web API stream;
- XPPython3 projects such as q4xpcc receive values inside X-Plane through
  simulator callbacks.

Both environments will depend on `xplane-fdr`. `xplane-fdr` will depend on
neither. There will be one implementation of the models, parsers, writers,
profiles, recording lifecycle, validation, and conversion behavior.

```text
                         native X-Plane FDR
                                  |
                          xplane_fdr core
                    sample -> session -> sink
                         ^                 |
                         |                 +-- FDR file
             +-----------+-----------+     +-- GeoJSON model
             |                       |
     xpwebapi Web API          XPPython3/XPLM
         adapter                  adapter
```

The package is X-Plane-specific but capture-neutral. DataRefs, FDR versions,
flight samples, and X-Plane units belong in the domain. HTTP, WebSockets,
XPLM callbacks, plugin lifecycles, and consumer-specific business rules do not.

## Goals

- Read and validate X-Plane FDR versions 3 and 4.
- Generate deterministic canonical version 4 FDR files.
- Record samples supplied by callback-driven or pull-driven capture adapters.
- Preserve known and unknown metadata without silently discarding it.
- Preserve each optional DataRef's conversion factor and comment.
- Provide reusable stock-X-Plane recording profiles and strict JSON
  configuration.
- Provide configurable artifact storage with an X-Plane 12-oriented default
  directory and deterministic filename fallback.
- Export standards-conforming GeoJSON.
- Make every core behavior testable without X-Plane, XPPython3, a network,
  sleeping, or third-party packages.
- Support installation into the Python environment embedded by XPPython3.
- Give consumers stable composition interfaces without runtime plugin
  discovery.

## Non-Goals

- Supporting simulators other than X-Plane.
- Hosting or loading XPLM, XPPython3, or native simulator plugins.
- Connecting to the X-Plane Web API.
- Providing HTTP, WebSocket, GUI, or simulator orchestration behavior.
- Providing a general telemetry framework.
- Discovering capture providers through package entry points.
- Writing version 3 FDR files.
- Converting X-Plane `.rep` files.
- Guaranteeing that X-Plane or a third-party plugin can replay every recorded
  DataRef.
- Adding landing scoring, OOOI detection, ACARS reporting, or aircraft-specific
  operational logic.

## Compatibility Contract

The distribution will declare Python 3.12 or newer and no runtime
dependencies:

```toml
requires-python = ">=3.12"
dependencies = []
```

It will produce a pure-Python `py3-none-any` wheel. Importing `xplane_fdr`
will perform no network access, start no thread, inspect no simulator state,
and import no adapter package. Core operation will use only the Python standard
library.

The compatibility claim covers ordinary CPython and the Python 3.12 runtime
provided for XPPython3. The package will not import `xp` or XPLM modules, so the
same artifact remains usable by offline tools and external clients.

## Package Architecture

The initial implementation will use focused modules with one-way dependencies:

```text
xplane_fdr/
|-- __init__.py       stable supported imports
|-- errors.py         public FDR and configuration exceptions
|-- models.py         immutable metadata, declarations, samples, recordings
|-- reader.py         incremental FDR v3/v4 parsing and validation
|-- writer.py         deterministic v4 serialization and streaming sink
|-- recording.py      push-first recording session and composition protocols
|-- profiles.py       immutable stock-X-Plane profile definitions
|-- config.py         strict adapter-neutral JSON configuration
|-- geojson.py        JSON-compatible GeoJSON conversion
|-- cli.py            offline inspect, validate, and conversion commands
`-- schemas/
    `-- fdr-record-config-v1.schema.json
```

`xplane_fdr.__init__` will explicitly export the supported public surface.
Command-line code will call the same public library behavior; it will not
contain a second parser, writer, validator, or converter.

Adapters belong to their owning projects. For example, `xpwebapi` will contain
its Web API source and live-record command, while q4xpcc may contain an XPLM
source. Consumer adapters translate their native observations into
`xplane_fdr` models.

## Data Model

An `FDRRecording` will contain:

- source format version `3` or `4`;
- source origin marker `A` or `I`;
- ordered comments;
- ordered known and unknown metadata fields;
- ordered `FDRDataref` declarations containing a path, finite conversion
  factor, and optional comment;
- for version 3 input, ordered legacy fixed-column declarations and values
  separate from version 4 `DREF` declarations;
- ordered samples;
- the unzoned local calendar date from `DATE`, when present.

Version 4 mandatory sample fields are UTC time, longitude, latitude, altitude
above mean sea level in feet, magnetic heading, pitch, and roll. Additional
`DREF` fields remain ordered and hold finite numeric source values. A version 4
conversion factor belongs to its declaration; it is not pre-applied to the
stored sample.

Version 3 uses Laminar Research's legacy fixed-column `DATA` layout. The reader
will preserve positional values, resolve elapsed seconds from the Zulu start
time in `TIME`, and expose documented position and attitude fields through the
common navigation view. Legacy-only fields will not be mislabeled as DataRefs.

Models will reject booleans where numbers are required, non-finite numbers,
invalid coordinates, duplicate identifiers, row-width mismatches, and invalid
time ordering. Models will be safe to construct directly for deterministic
fixtures.

FDR supplies an unzoned local `DATE` and UTC times of day but no UTC offset.
The reader will preserve these separately rather than inventing an absolute
timestamp. It may count an observed midnight rollover for duration. A caller
that needs absolute instants must provide the first UTC calendar date.

## Recording Boundary

The primary recording API will be push-oriented because simulator plugins are
callback-driven:

```python
with FDRRecordingSession.open(path, definition) as session:
    session.record(sample)
```

`record(sample)` will validate and append one semantic FDR sample. It will not
sleep, open a connection, poll a source, or start a background thread. The
capture adapter owns scheduling and constructs samples from its environment.

This permits:

- an XPPython3 flight-loop callback to call `record()` directly;
- a WebSocket receive or sampling loop to call the same method;
- an offline replay or test harness to submit deterministic samples.

Small `FDRSampleSource` and `FDRSampleSink` protocols will remain available for
composition. A pull-oriented `record_from(source)` convenience may consume a
source iterator, but it will be implemented on top of the push-first session.
The source protocol will expose semantic FDR samples and will not mention Web
API observation identifiers, XPLM handles, or a particular concurrency model.

Path-based sessions will write to a uniquely created sibling partial file. A
graceful close after at least one valid sample will flush and synchronize the
file before atomically moving it to the destination. Unexpected failure will
preserve the partial artifact for diagnosis and will never publish it under the
requested final name. Failures before the first sample will not appear to be
successful recordings.

Existing destinations will be rejected unless overwrite is explicitly enabled.
Caller-supplied streams remain under caller ownership and durability control.

Callers may supply a complete destination path, or they may resolve one from
the recording configuration. A complete caller-supplied path has highest
precedence. A caller-supplied filename uses the configured directory and
overrides a configured filename. When neither is supplied, the library uses
the configured filename or generates
`xplane-fdr-YYYYMMDDTHHMMSSffffffZ.fdr` from the recording's UTC start instant.
The start instant may be supplied directly, and the clock used when it is
omitted will be replaceable so filename behavior remains deterministic in
tests.

The configured storage directory defaults to `Output/FDR files`, interpreted
relative to an X-Plane installation root supplied by the adapter. This is the
library's X-Plane 12 storage convention; the core will not search for an
installation or import simulator APIs to discover it. Explicit absolute
directories are also valid. A configured filename is a literal basename
ending in `.fdr`, not a template, and may not contain a directory separator.
Overwrite permission is never read from reusable configuration and must remain
an explicit API or command-line decision.

## Reader and Writer Behavior

The reader will parse incrementally and report structural failures with source
line numbers. It will accept origin `A` or `I`, parse version suffix text,
preserve ordered comments and metadata, retain unknown four-character metadata
keys, and derive row schemas from the applicable format.

Every version 4 row must contain seven mandatory values plus one value for each
ordered `DREF`. Every version 3 row must match its documented fixed layout.
Malformed numbers, timestamps, declarations, and widths are errors rather than
warnings printed by library code.

The writer will serialize valid version 4 data deterministically as UTF-8 with
LF separators and the canonical `A\n4\n` prefix. It will never derive field
order, clocks, dates, or aircraft identity from ambient process state.

A version 3 recording may be normalized to version 4 only through an explicit
lossy-conversion opt-in when legacy-only columns would be omitted. The result
will retain the common navigation view and report omitted fields.

## Recording Profiles and Configuration

Built-in profiles will contain only verified stock `sim/...` DataRefs. The
initial profiles are `minimal`, `standard`, `systems`, `avionics`, and `full`.
They are immutable ordered manifests. `full` is shorthand for the ordered
union of the other non-minimal profiles.

Every version 4 recording contains the mandatory trajectory spine. Profile and
custom DataRefs add ordered `DREF` declarations. Aircraft- and plugin-specific
paths are supplied through project-owned JSON rather than built into the
package.

The reusable JSON contract is adapter-neutral. It may describe profiles,
sampling policy, FDR metadata, custom DataRefs, and artifact storage. Storage
has a `directory` and an optional literal `filename`:

```json
{
  "storage": {
    "directory": "Output/FDR files",
    "filename": "training-flight.fdr"
  }
}
```

The directory defaults to `Output/FDR files`. Relative directories are
resolved against an X-Plane installation root supplied by the adapter;
absolute directories require no simulator root. The filename is optional and
follows the precedence and generated-name rules in the recording boundary.
The configuration will not contain host, port, WebSocket path, XPLM callback,
or overwrite policy. Adapter projects may compose it into an outer
configuration that adds their own connection or lifecycle settings.

Configuration loading will use `json` plus explicit standard-library semantic
validation. The packaged JSON Schema supports editors and external validators
but creates no runtime dependency. Unknown properties and unsupported schema
versions are errors.

## GeoJSON Behavior

GeoJSON conversion will return a JSON-compatible `FeatureCollection`. Each
sample will produce a point feature, and a final line feature will describe the
ordered path when at least two locations exist.

Coordinates use longitude then latitude. Because FDR altitude is MSL while the
third GeoJSON coordinate has different geodetic semantics, geometry will remain
two-dimensional. Point properties will include `altitude_msl_ft`, its explicit
metre conversion, time of day, attitude, and additional DataRef values.

An RFC 3339 timestamp is emitted only when the caller supplies enough UTC-date
information. Paths crossing the antimeridian will be split into a
`MultiLineString`; other paths use a `LineString`.

The converter returns data and does not choose an output path. File creation
and JSON serialization remain application or CLI responsibilities.

## Command-Line Boundary

The standalone distribution will provide offline commands for:

- `inspect`: summarize metadata, declarations, sample count, times, and
  duration;
- `validate`: strictly parse and validate an FDR file;
- `to-geojson`: convert a valid recording to GeoJSON.

The core package will not offer a source-specific live-record command.
`xpwebapi-fdr record` remains in `xpwebapi` because connection and capture are
Web API responsibilities. An XPPython3 project may expose its own simulator UI
or command without changing the core.

Commands use status zero for success and nonzero for argument, input,
validation, conversion, or output failures. Diagnostics go to standard error.
Existing output is protected unless overwrite is explicit.

## XPPython3 Consumption

The preferred deployment installs the released `xplane-fdr` wheel into
XPPython3's Python `site-packages` using its supported pip facilities. The
package itself will not invoke pip or download code. A consumer may provide an
explicit installer or bootstrap step and should pin or bound the compatible
version.

A plugin distribution may bundle an exact released copy as an offline fallback
when its deployment workflow requires it. Such bundling is a packaging action,
not a source fork: changes remain authored, tested, versioned, and released in
`xplane-fdr`.

An XPPython3 adapter will resolve and read DataRefs through XPLM, construct a
semantic FDR sample, and submit it to `FDRRecordingSession.record()` from an
appropriate flight-loop callback. It will not be part of this repository.

## Error Handling

The public exception hierarchy will distinguish parse, semantic validation,
configuration, recording-state, and output failures. Exceptions will carry
structured context such as source name, line number, JSON property path, or
artifact path where applicable. Library code will not print diagnostics or
terminate the process.

Recording-session state transitions will be explicit. Recording before open,
recording after close, double commit, and commit without a valid sample are
errors. Cleanup failures will not hide an earlier primary failure; both will be
available to the caller.

## Testing and Verification

Automated tests will use `unittest`. Verification will include:

- valid version 3 and version 4 reference fixtures;
- both origin markers and common line separators;
- malformed markers, versions, metadata, declarations, rows, coordinates,
  times, and numbers;
- conversion-factor and comment preservation;
- deterministic writer bytes and read/write round trips;
- version 3 preservation and explicit lossy v3-to-v4 normalization;
- push-driven sessions called like simulator callbacks;
- pull-source composition implemented through the same session API;
- atomic output, overwrite protection, partial recovery, and failure ordering;
- immutable profile definitions and deterministic composition;
- strict configuration parsing and packaged schema availability;
- storage-directory resolution, configured and caller-supplied filename
  precedence, deterministic default naming, and configured-basename
  validation;
- valid GeoJSON, coordinate order, MSL properties, UTC-date resolution, and
  antimeridian splitting;
- CLI output, exit status, stream separation, and overwrite behavior;
- import tests proving the absence of adapter and third-party dependencies;
- wheel and source-distribution inspection;
- installed-wheel smoke tests on Python 3.12 and later supported versions.

Simulator and Web API tests belong to adapter projects. They may supplement but
will not replace deterministic core verification.

## Repository and Release Contract

The new repository will adopt the established engineering workflow used by
`xplane-webapi`, adjusted for this smaller dependency-free package:

- repository instructions and local workflow skills;
- design specifications and implementation plans under `docs/superpowers/`;
- `uv`-managed packaging and a committed lockfile;
- Ruff, type checking, coverage, security, documentation, and hygiene gates;
- `unittest` as the only test framework;
- wheel and source-distribution verification;
- trusted publishing to PyPI;
- MIT licensing with all required attribution preserved.

`xplane-fdr` will release independently. Adapter projects will declare an
intentional compatible version range and update through their normal release
process. The core will follow semantic versioning and treat documented imports,
configuration schemas, native serialization behavior, and exception contracts
as public compatibility surfaces.

## Migration from xpwebapi

The existing unreleased FDR implementation on the `xpwebapi` feature branch
will be moved and refactored before either project releases the feature:

1. Establish this repository's packaging, quality, and documentation baseline.
2. Move neutral models, errors, reader, writer, recording session, profiles,
   configuration, GeoJSON, fixtures, and offline CLI behavior here.
3. Refactor recording around the push-first session while retaining optional
   source/sink composition.
4. Publish and verify an initial `xplane-fdr` release.
5. Make `xpwebapi` depend on that release.
6. Retain only the Web API capture adapter and live-record integration in
   `xpwebapi`.
7. Update `xpwebapi` documentation and release it as the planned minor feature
   release.

There will be no duplicated implementation. Because the `xpwebapi.fdr` public
surface has not yet been released, compatibility re-exports are optional and
will be included only when they materially improve the adapter experience.

## Success Criteria

The design succeeds when:

- `xplane-fdr` installs with no runtime dependencies;
- the same recording session accepts samples from a deterministic test, a Web
  API adapter, and an XPPython3-style callback adapter;
- native FDR read/write and GeoJSON behavior live in only one distribution;
- `xpwebapi` contains no duplicate FDR parser, writer, profiles, or conversion
  code;
- an XPPython3 consumer can install the universal wheel and import the package
  without loading any network or plugin-host dependency;
- both repositories pass their documented quality and artifact gates before
  release.
