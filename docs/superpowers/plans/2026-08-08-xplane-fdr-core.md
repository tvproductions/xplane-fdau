# xplane-fdr Core Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build and verify the independently releasable `xplane-fdr` standard-library-only package for X-Plane FDR v3/v4 reading, canonical v4 writing, push-first recording, configuration, profiles, GeoJSON, and offline commands.

**Architecture:** Move only capture-neutral behavior from the unreleased `xpwebapi` FDR branch at commit `ca7d621`, then refactor recording around `FDRRecordingSession.record(sample)`. Keep dependencies one-way from errors and immutable models into readers, writers, recording, profiles, configuration, GeoJSON, and the thin CLI; capture adapters remain in their owning projects.

**Tech Stack:** Python 3.12+ standard library at runtime, `uv`/`uv_build` for packaging, Python `unittest`, Ruff, ty, coverage, Bandit, detect-secrets, MkDocs, and GitHub Actions as development-only tooling.

## Global Constraints

- Distribution: `xplane-fdr`; import package: `xplane_fdr`; initial version: `0.1.0`.
- Declare `requires-python = ">=3.12"`, `dependencies = []`, and build a pure-Python `py3-none-any` wheel.
- Runtime code may import only the Python standard library and other `xplane_fdr` modules.
- Never import or depend on `xpwebapi`, XPPython3, `xp`, XPLM, or a network client.
- Python's `unittest` is the only test framework; all commands use `python -m unittest`.
- Write only canonical FDR v4; v3 is input-only and normalization requires explicit lossy opt-in.
- Preserve ordered comments, metadata, declarations, values, conversion factors, and comments.
- Do not copy GPL implementation from `hotbso/xgs` or redistribute full Laminar fixtures.
- Preserve MIT attribution when moving code authored in `xplane-webapi`.
- No push, tag, PyPI publication, or GitHub release occurs without explicit user authorization.
- The later `xpwebapi` adapter migration is a separate plan after an `xplane-fdr` wheel is release-ready.

---

### Task 1: Bootstrap the Distribution and Runtime Boundary

**Files:**
- Create: `pyproject.toml`
- Create: `.python-version`
- Create: `uv.lock`
- Create: `xplane_fdr/__init__.py`
- Create: `xplane_fdr/py.typed`
- Create: `tests/__init__.py`
- Create: `tests/test_project_metadata.py`
- Modify: `LICENSE`

**Interfaces:**
- Produces importable `xplane_fdr` with `__version__ = "0.1.0"`.
- Produces project metadata with no runtime requirements and `uv_build` using `module-root = ""`.
- Preserves the existing TV Productions copyright and adds the inherited MIT attribution lines from the source repository.

- [ ] **Step 1: Write the failing metadata contract test**

```python
from pathlib import Path
import tomllib
import unittest


class ProjectMetadataTests(unittest.TestCase):
    def test_distribution_contract_is_dependency_free(self) -> None:
        project = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))["project"]
        self.assertEqual("xplane-fdr", project["name"])
        self.assertEqual("0.1.0", project["version"])
        self.assertEqual(">=3.12", project["requires-python"])
        self.assertEqual([], project["dependencies"])

    def test_runtime_package_exposes_matching_version(self) -> None:
        import xplane_fdr

        self.assertEqual("0.1.0", xplane_fdr.__version__)
```

- [ ] **Step 2: Run the test to verify the missing project metadata failure**

Run: `python -m unittest tests.test_project_metadata -v`

Expected: ERROR because `pyproject.toml` and `xplane_fdr` do not exist.

- [ ] **Step 3: Create the minimal package metadata**

Use this project contract in `pyproject.toml`:

```toml
[project]
name = "xplane-fdr"
version = "0.1.0"
description = "A standard-library-only Python toolkit for reading, writing, recording, validating, and converting X-Plane Flight Data Recorder files, independent of how flight data is captured."
readme = "README.md"
license = "MIT"
license-files = ["LICENSE"]
requires-python = ">=3.12"
dependencies = []

[build-system]
requires = ["uv_build>=0.11.26,<0.12"]
build-backend = "uv_build"

[tool.uv.build-backend]
module-root = ""
```

Add Python 3.12, 3.13, and 3.14 classifiers, project URLs for `tvproductions/xplane-fdr`, and development dependency groups copied by capability—not package runtime—from `xplane-webapi`.

Use this development-only group:

```toml
[dependency-groups]
dev = [
    "bandit>=1.9.4",
    "cohesion>=1.2.0",
    "coverage>=7.14.1",
    "detect-secrets>=1.5.0",
    "interrogate>=1.7.0",
    "lizard>=1.23.0",
    "mkdocs",
    "mkdocs-git-revision-date-localized-plugin",
    "mkdocs-material",
    "mkdocstrings",
    "mkdocstrings-python",
    "pre-commit>=4.5.1",
    "pyyaml>=6.0.3",
    "ruff>=0.15.17",
    "ty>=0.0.49",
    "vulture>=2.16",
    "wily>=1.12.2",
    "xenon>=0.9.3",
]
```

- [ ] **Step 4: Add the runtime version and attribution**

Set `xplane_fdr.__version__ = "0.1.0"` and export only `__version__` initially. Add the inherited MIT copyright lines for Pierre Mareschal and Pierre M above the existing 2026 TV Productions line in `LICENSE`.

- [ ] **Step 5: Lock, synchronize, and rerun the metadata test**

```powershell
uv lock
uv sync --frozen --python 3.12
uv run --python 3.12 python -m unittest tests.test_project_metadata -v
```

Expected: PASS with two tests and no runtime dependency entries in installed metadata.

- [ ] **Step 6: Commit the package bootstrap**

```powershell
git add pyproject.toml .python-version uv.lock xplane_fdr tests LICENSE
git commit -m "build: bootstrap xplane-fdr package"
```

---

### Task 2: Establish Quality, CI, and Project Workflow Controls

**Files:**
- Create: `.pre-commit-config.yaml`
- Create: `.secrets.baseline`
- Create: `.github/dependabot.yml`
- Create: `.github/workflows/ci.yml`
- Create: `tools/quality.py`
- Create: `tests/test_quality_tool.py`
- Create: `tests/test_project_skills.py`
- Create: `.codex/skills/code-quality/SKILL.md`
- Create: `.codex/skills/hygiene/SKILL.md`
- Create: `.codex/skills/hygiene/scripts/hygiene.py`
- Create: `.codex/skills/git-sync/SKILL.md`
- Modify: `pyproject.toml`
- Modify: `uv.lock`

**Interfaces:**
- Produces `python tools/quality.py check` as the local blocking gate.
- Produces CI compatibility coverage on Python 3.12, 3.13, and 3.14.
- Produces project-specific quality, hygiene, git-sync, documentation, and release skills without copying the old project's text verbatim.

- [ ] **Step 1: Write failing quality-runner and skill-contract tests**

```python
class QualityToolTests(unittest.TestCase):
    def test_check_uses_unittest_and_all_blocking_gates(self) -> None:
        names = tuple(step.name for step in quality.CHECK_STEPS)
        self.assertIn("unittest", names)
        self.assertIn("ruff check", names)
        self.assertIn("ty check", names)
        self.assertNotIn("xpwebapi", " ".join(" ".join(step.command) for step in quality.CHECK_STEPS))


class ProjectSkillTests(unittest.TestCase):
    def test_project_skills_are_scoped_to_xplane_fdr(self) -> None:
        for name in ("code-quality", "hygiene", "git-sync"):
            path = Path(".codex/skills") / name / "SKILL.md"
            text = path.read_text(encoding="utf-8")
            self.assertIn("name:", text)
            self.assertNotIn("xpwebapi", text.lower())
```

- [ ] **Step 2: Run focused tests and confirm the controls are missing**

Run: `uv run python -m unittest tests.test_quality_tool tests.test_project_skills -v`

Expected: ERROR because the quality module and project skills do not exist.

- [ ] **Step 3: Implement the repository quality runner**

Adapt `tools/quality.py` from the source repository so `SOURCE_PATHS = ("xplane_fdr", "tests", "tools")`. Its blocking `check` sequence is Ruff lint, Ruff format check, ty, `python -m unittest discover -v`, coverage with a ratchetable initial minimum of 40%, Bandit over `xplane_fdr`, detect-secrets, Interrogate, Vulture, and Xenon. Keep metrics and Wily as explicit nonblocking subcommands.

Configure coverage source as `xplane_fdr`, Ruff line length as 160 with `E`, `F`, and `W` lint families, and ty with `all = "error"`. Any narrow ty exception must include a comment naming the pre-existing code pattern it permits; do not disable the type checker globally.

- [ ] **Step 4: Author project-local skills through the writing-skills workflow**

Invoke `writing-skills` before creating these files. Each skill must call the actual `xplane-fdr` commands, explain when it applies, and avoid network or simulator assumptions.

- [ ] **Step 5: Add CI, release, dependency, and pre-commit configuration**

At this stage CI runs the quality gate and `unittest` compatibility jobs on Python 3.12, 3.13, and 3.14. Artifact and tag jobs are added only after their tooling exists in Task 14.

- [ ] **Step 6: Run focused tests and the currently available gates**

```powershell
uv lock
uv sync --frozen
uv run python -m unittest tests.test_quality_tool tests.test_project_skills -v
uv run ruff check tools tests
uv run ruff format --check tools tests
```

- [ ] **Step 7: Commit the workflow baseline**

```powershell
git add .github .pre-commit-config.yaml .secrets.baseline .codex/skills tools tests pyproject.toml uv.lock
git commit -m "build: establish project quality workflows"
```

---

### Task 3: Establish Verified Minimal FDR Fixtures

**Files:**
- Create: `tests/fixtures/fdr/README.md`
- Create: `tests/fixtures/fdr/version3-minimal.fdr`
- Create: `tests/fixtures/fdr/version4-minimal.fdr`
- Create: `tests/fixtures/fdr/inherited-recorder-minimal.fdr`
- Create: `tests/test_fdr_fixtures.py`

**Interfaces:**
- Consumes Laminar's installed `Instructions/FDR Example Version 3.fdr`, the official v3 field documentation, and the v4 reference shape.
- Produces small independently minimized fixtures with documented source version, fixed width, navigation indices, line endings, and synthetic sample values.

- [ ] **Step 1: Locate and record the v3 evidence before parser work**

Locate `Instructions/FDR Example Version 3.fdr` in a licensed X-Plane 12 installation. Record the X-Plane build, source path, first two header lines, record kinds, fixed column count, and indices for elapsed seconds, longitude, latitude, MSL altitude, magnetic heading, pitch, and roll in the fixture README. If unavailable, stop this task and request the file; do not infer the layout from v4 or online fragments.

- [ ] **Step 2: Write the failing fixture contract test**

```python
FIXTURE_ROOT = Path(__file__).parent / "fixtures" / "fdr"


class FDRFixtureTests(unittest.TestCase):
    def test_minimal_fixtures_and_provenance_are_committed(self) -> None:
        for name in ("version3-minimal.fdr", "version4-minimal.fdr", "inherited-recorder-minimal.fdr"):
            with self.subTest(name=name):
                self.assertTrue((FIXTURE_ROOT / name).is_file())
        provenance = (FIXTURE_ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("Laminar Research", provenance)
        self.assertIn("independently minimized", provenance)
```

- [ ] **Step 3: Run the test to confirm fixtures are missing**

Run: `uv run python -m unittest tests.test_fdr_fixtures -v`

Expected: FAIL because the fixture files are absent.

- [ ] **Step 4: Construct the minimal fixtures**

The v4 fixture contains two samples, one `DREF` with scale `2.0` and a comment, exact prefix `A\n4\n`, and synthetic Chicago-area coordinates. The inherited fixture preserves valid mixed separator/header spacing produced by the old recorder. The v3 fixture retains the verified official row width and field order but replaces all sample values with synthetic values. Do not copy the full 563 KB official v4 sample or the full installed v3 sample.

- [ ] **Step 5: Run the fixture test and inspect bytes**

```powershell
uv run python -m unittest tests.test_fdr_fixtures -v
uv run python -c "from pathlib import Path; data=Path('tests/fixtures/fdr/version4-minimal.fdr').read_bytes(); assert data.startswith(b'A\n4\n'); assert b'\r' not in data"
```

- [ ] **Step 6: Commit the fixture evidence**

```powershell
git add tests/fixtures/fdr tests/test_fdr_fixtures.py
git commit -m "test: add verified fdr format fixtures"
```

---

### Task 4: Implement Immutable Models and Structured Exceptions

**Files:**
- Create: `xplane_fdr/errors.py`
- Create: `xplane_fdr/models.py`
- Create: `tests/test_fdr_models.py`
- Modify: `xplane_fdr/__init__.py`

**Interfaces:**
- Produces `FDRError`, `FDRParseError`, `FDRValidationError`, `FDRConfigError`, `FDRRecordingStateError`, and `FDROutputError` with structured optional context.
- Produces immutable `FDRMetadata`, `FDRDataref`, `FDRLegacyColumn`, `FDRHeader`, `FDRSample`, `FDRRecording`, and `FDRNormalizationResult`.

- [ ] **Step 1: Write failing construction, validation, and context tests**

```python
sample = FDRSample(
    time_utc=time(23, 59, 59, 500000),
    longitude=-87.9048,
    latitude=41.9742,
    altitude_msl_ft=640,
    heading_magnetic_deg=270,
    pitch_deg=2,
    roll_deg=-1,
    additional_values=(0.75,),
    legacy_values=(),
)
self.assertEqual(time(23, 59, 59, 500000), sample.time_utc)
with self.assertRaises(FDRValidationError):
    dataclasses.replace(sample, longitude=True)
error = FDRParseError("bad row", source="flight.fdr", line=12)
self.assertEqual(("flight.fdr", 12), (error.source, error.line))
```

Cover tuple freezing, duplicate identifiers, row-width mismatch, invalid dates, invalid coordinates, booleans, non-finite values, exact arbitrary-size integers, midnight duration, explicit UTC-date resolution, and lossy normalization omissions.

- [ ] **Step 2: Run tests to verify imports fail**

Run: `uv run python -m unittest tests.test_fdr_models -v`

Expected: ERROR because model and exception classes are not exported.

- [ ] **Step 3: Implement the exception hierarchy**

Every exception stores `message`, plus applicable `source`, `line`, `property_path`, and `artifact_path`. Formatting includes only provided context. `FDROutputError` retains the original `OSError` through exception chaining; cleanup plus primary failures use `BaseExceptionGroup`.

- [ ] **Step 4: Move and harden the neutral immutable models**

Port the neutral logic from `xpwebapi/fdr/models.py` at `ca7d621`, rename imports to `xplane_fdr`, and retain frozen slotted dataclasses. Use `type(value) is int` or `type(value) is float` before `math.isfinite` so booleans are rejected. Keep v3 legacy values separate from v4 additional DataRef values.

- [ ] **Step 5: Export only completed public types and run checks**

```powershell
uv run python -m unittest tests.test_fdr_models -v
uv run ruff check xplane_fdr tests/test_fdr_models.py
uv run ruff format --check xplane_fdr tests/test_fdr_models.py
uv run ty check
```

- [ ] **Step 6: Commit models and errors**

```powershell
git add xplane_fdr tests/test_fdr_models.py
git commit -m "feat: add immutable fdr domain models"
```

---

### Task 5: Parse Version 4 Incrementally

**Files:**
- Create: `xplane_fdr/reader.py`
- Create: `tests/test_fdr_reader.py`
- Modify: `xplane_fdr/__init__.py`

**Interfaces:**
- Produces `FDRReader.open(source) -> FDRSampleStream` and `FDRReader.read(source) -> FDRRecording`.
- `source` accepts `str | os.PathLike[str] | TextIO`; path-opened streams are owned and caller streams remain open.

- [ ] **Step 1: Write failing v4 streaming and malformed-input tests**

```python
reader = FDRReader()
with reader.open(FIXTURE_ROOT / "version4-minimal.fdr") as stream:
    self.assertEqual(4, stream.header.source_version)
    first = next(stream)
    self.assertEqual(-87.9048, first.longitude)
self.assertEqual(2, len(reader.read(FIXTURE_ROOT / "version4-minimal.fdr").samples))
```

Cover `A` and `I`, version suffix text, CR/LF/CRLF, short chunk reads, unknown four-character metadata, duplicate metadata with last-value lookup, comments, DataRef scale/comment, exact integer lexemes, timestamp microseconds, malformed markers/declarations/numbers/times/widths, header records after samples, and source line context.

- [ ] **Step 2: Run tests and confirm the reader is missing**

Run: `uv run python -m unittest tests.test_fdr_reader -v`

Expected: ERROR because `FDRReader` and `FDRSampleStream` are unavailable.

- [ ] **Step 3: Port one incremental v4 parser**

Port neutral behavior from `xpwebapi/fdr/reader.py` at `ca7d621`. Normalize CR, LF, and CRLF in bounded chunks; parse the header eagerly; yield samples lazily. Keep one parser shared by `open()` and `read()`. Convert model failures into typed errors retaining the source and line.

- [ ] **Step 4: Enforce stream ownership and strict number grammar**

Open paths as UTF-8 text with universal newline handling and close them on failure or context exit. Never close caller streams. Accept decimal/exponent integers and floats supported by the FDR grammar, reject Python-only numeric forms and all non-finite values.

- [ ] **Step 5: Run reader/model tests and checks**

```powershell
uv run python -m unittest tests.test_fdr_models tests.test_fdr_reader -v
uv run ruff check xplane_fdr tests/test_fdr_reader.py
uv run ruff format --check xplane_fdr tests/test_fdr_reader.py
```

- [ ] **Step 6: Commit v4 reading**

```powershell
git add xplane_fdr tests/test_fdr_reader.py
git commit -m "feat: parse fdr version 4 recordings"
```

---

### Task 6: Add Evidence-Backed Version 3 Parsing

**Files:**
- Modify: `xplane_fdr/reader.py`
- Modify: `xplane_fdr/models.py`
- Modify: `tests/test_fdr_reader.py`
- Modify: `tests/test_fdr_models.py`

**Interfaces:**
- Consumes the exact v3 width and navigation indices recorded in `tests/fixtures/fdr/README.md`.
- Produces common navigation fields plus aligned `FDRLegacyColumn` and `legacy_values` preservation.

- [ ] **Step 1: Add failing v3 fixture and malformed-width tests**

```python
recording = FDRReader().read(FIXTURE_ROOT / "version3-minimal.fdr")
self.assertEqual(3, recording.header.source_version)
self.assertEqual(len(recording.header.legacy_columns), len(recording.samples[0].legacy_values))
self.assertEqual(-87.9048, recording.samples[0].longitude)
```

Assert the fixture's documented synthetic longitude, latitude, MSL altitude, magnetic heading, pitch, and roll values through both the common navigation fields and their recorded legacy positions. Cover required `TIME`, elapsed-seconds resolution, midnight rollover, version suffixes, retained positional values, malformed widths, and line-numbered failures.

- [ ] **Step 2: Run the focused test and verify v3 is rejected**

Run: `uv run python -m unittest tests.test_fdr_reader tests.test_fdr_models -v`

Expected: FAIL because the reader supports only v4.

- [ ] **Step 3: Implement a separate v3 grammar branch**

Define the verified fixed schema as an ordered tuple of `FDRLegacyColumn` values. Do not pass v3 rows through the v4 `7 + len(datarefs)` rule. Parse elapsed seconds from the fixed first field, combine it with the Zulu `TIME` header, map only documented navigation indices to the common fields, and preserve every positional number in `legacy_values`.

- [ ] **Step 4: Verify explicit lossy conversion**

`FDRRecording.normalized_v4()` raises unless `allow_lossy_legacy=True`; the opt-in result lists every omitted legacy identifier in original order and retains common navigation samples.

- [ ] **Step 5: Run all fixture, model, and reader tests**

```powershell
uv run python -m unittest tests.test_fdr_fixtures tests.test_fdr_models tests.test_fdr_reader -v
uv run ruff check xplane_fdr tests/test_fdr_reader.py tests/test_fdr_models.py
```

- [ ] **Step 6: Commit v3 parsing**

```powershell
git add xplane_fdr tests/test_fdr_reader.py tests/test_fdr_models.py
git commit -m "feat: parse legacy fdr version 3"
```

---

### Task 7: Write Canonical Version 4 Durably

**Files:**
- Create: `xplane_fdr/writer.py`
- Create: `tests/test_fdr_writer.py`
- Modify: `xplane_fdr/__init__.py`

**Interfaces:**
- Produces `FDRWriter.open(header, destination, *, overwrite=False) -> FDRStreamWriter`.
- Produces `FDRWriter.write(recording, destination, *, overwrite=False, allow_lossy_legacy=False) -> FDRNormalizationResult`.
- `FDRStreamWriter` exposes `write_sample`, `commit`, `abort`, `sample_count`, `destination_path`, and `partial_path`.

- [ ] **Step 1: Write failing canonical and failure-ordering tests**

```python
destination = self.directory / "flight.fdr"
result = FDRWriter().write(recording, destination)
self.assertEqual(b"A\n4\n", destination.read_bytes()[:4])
self.assertEqual(recording, FDRReader().read(destination))
self.assertEqual((), result.omitted_legacy_field_ids)
```

Cover exact UTF-8 LF bytes, stable metadata/comment/DataRef order, finite number rendering, complete/streaming parity, caller stream ownership, width rejection, v3 refusal and lossy opt-in, existing target protection, overwrite only at commit, fsync, partial preservation, zero-sample commit, and grouped cleanup failures.

- [ ] **Step 2: Run tests and confirm writer imports fail**

Run: `uv run python -m unittest tests.test_fdr_writer -v`

Expected: ERROR because writer classes are unavailable.

- [ ] **Step 3: Port one canonical serializer**

Port the neutral serializer from `xpwebapi/fdr/writer.py` at `ca7d621`. Both complete and streaming paths call the same header/sample renderers. Always emit `A\n4\n`; never derive clocks, dates, field order, or aircraft identity from ambient state.

- [ ] **Step 4: Implement durable path publication**

Validate the full header before creating output. Create a unique sibling `.<name>.<token>.partial` exclusively. After at least one valid sample, flush, `os.fsync`, close, then publish without replacement using same-volume link/unlink when `overwrite=False`, or `os.replace` when `overwrite=True`. Wrap output failures in `FDROutputError` with `artifact_path`; preserve diagnostic partials.

- [ ] **Step 5: Preserve caller stream ownership**

For caller streams, write and flush but never close or call `fileno`/`fsync`. Context exit without explicit commit aborts. If body and cleanup both fail, raise a `BaseExceptionGroup` containing both in primary-first order.

- [ ] **Step 6: Run writer and reader verification**

```powershell
uv run python -m unittest tests.test_fdr_reader tests.test_fdr_writer -v
uv run ruff check xplane_fdr tests/test_fdr_writer.py
uv run ruff format --check xplane_fdr tests/test_fdr_writer.py
```

- [ ] **Step 7: Commit canonical writing**

```powershell
git add xplane_fdr tests/test_fdr_writer.py
git commit -m "feat: write canonical fdr version 4"
```

---

### Task 8: Implement Push-First Recording Sessions and Storage Resolution

**Files:**
- Create: `xplane_fdr/recording.py`
- Create: `tests/test_fdr_recording.py`
- Modify: `xplane_fdr/__init__.py`

**Interfaces:**
- Produces immutable `FDRSamplingPolicy`, `FDRStoragePolicy`, and `FDRRecordingDefinition`.
- Produces `FDRSampleSource` and `FDRSampleSink` protocols.
- `FDRSamplingPolicy(interval_seconds: float = 0.1, duration_seconds: float | None = None)` and `FDRStoragePolicy(directory: Path = Path("Output/FDR files"), filename: str | None = None)` compose `FDRRecordingDefinition(header, sampling, storage)`.
- `FDRSampleSource.__iter__() -> Iterator[FDRSample]`; `FDRSampleSink` exposes `write_sample(FDRSample)`, `commit()`, `abort()`, `destination_path`, and `partial_path`.
- `FDRRecordingSession.open(destination: str | os.PathLike[str] | TextIO | None, definition: FDRRecordingDefinition, *, xplane_root: str | os.PathLike[str] | None = None, filename: str | None = None, started_at_utc: datetime | None = None, overwrite: bool = False, utc_clock: Callable[[], datetime] = utc_now) -> FDRRecordingSession`.
- The session exposes `record(sample)`, `record_from(source) -> int`, `commit() -> Path | None`, and `abort() -> None`.

- [ ] **Step 1: Write failing callback-style and state-machine tests**

```python
with FDRRecordingSession.open(destination, definition) as session:
    session.record(sample_one)
    session.record(sample_two)
self.assertEqual((sample_one, sample_two), FDRReader().read(destination).samples)

with self.assertRaises(FDRRecordingStateError):
    session.record(sample_one)
```

`open()` returns a prepared session; entering its context transitions it to active. Cover recording before context entry/after close, double commit, commit without samples, invalid width, UTC time-of-day with midnight rollover, exception-triggered abort, partial preservation, caller streams, and `record_from()` delegating each sample through `record()`.

- [ ] **Step 2: Write failing destination-precedence and naming tests**

```python
definition = FDRRecordingDefinition(
    header=header,
    sampling=FDRSamplingPolicy(interval_seconds=0.1, duration_seconds=None),
    storage=FDRStoragePolicy(directory=Path("Output/FDR files"), filename=None),
)
session = FDRRecordingSession.open(
    None,
    definition,
    xplane_root=self.directory,
    started_at_utc=datetime(2026, 8, 8, 18, 30, 12, 123456, tzinfo=UTC),
)
self.assertEqual("xplane-fdr-20260808T183012123456Z.fdr", session.destination_path.name)
```

Assert precedence: complete destination path, caller filename plus configured directory, configured filename, generated filename. Relative directories require `xplane_root`; absolute directories do not. Configured names must be basenames ending in `.fdr` with neither `/` nor `\`.
The generated form is exactly `xplane-fdr-YYYYMMDDTHHMMSSffffffZ.fdr`, using six UTC microsecond digits and no punctuation that is invalid in a Windows basename.

- [ ] **Step 3: Run tests and confirm the session API is missing**

Run: `uv run python -m unittest tests.test_fdr_recording -v`

Expected: ERROR because recording types are not exported.

- [ ] **Step 4: Implement the definition, protocols, and destination resolver**

`FDRSamplingPolicy` validates positive finite interval/duration values. `FDRStoragePolicy` defaults to `Path("Output/FDR files")` and no filename. `FDRRecordingDefinition` requires a v4 header. Destination resolution uses an explicit aware UTC `started_at_utc` or an injectable aware-UTC clock only for default naming; serialization remains ambient-state-free.

- [ ] **Step 5: Implement the session state machine over `FDRStreamWriter`**

`record()` performs only semantic validation and one sink append—no sleeping, polling, connection, thread, or event loop. Normal context exit commits after at least one sample; exceptional exit aborts. `record_from(source)` is a simple iterator convenience returning the number recorded.

- [ ] **Step 6: Run recording/writer tests and dependency-boundary checks**

```powershell
uv run python -m unittest tests.test_fdr_writer tests.test_fdr_recording -v
uv run python -c "import xplane_fdr.recording as r; forbidden={'xpwebapi','xp','websockets','httpx'}; import sys; assert forbidden.isdisjoint(sys.modules)"
uv run ruff check xplane_fdr tests/test_fdr_recording.py
```

- [ ] **Step 7: Commit push-first recording**

```powershell
git add xplane_fdr tests/test_fdr_recording.py
git commit -m "feat: add push-first recording sessions"
```

---

### Task 9: Add Immutable Stock Recording Profiles

**Files:**
- Create: `xplane_fdr/profiles.py`
- Create: `tests/test_fdr_profiles.py`
- Modify: `xplane_fdr/__init__.py`

**Interfaces:**
- Produces immutable `FDRTrajectorySource(field_name, dataref_path, multiplier)` and `mandatory_trajectory_sources()` for the six numeric v4 spine fields.
- Produces immutable `FDRRecordingProfile(name, description, datarefs)` plus `list_profiles()`, `get_profile(name)`, and `compose_profiles(names)`.
- Profile composition preserves first appearance and rejects unknown names.

- [ ] **Step 1: Write failing exact-membership and immutability tests**

```python
self.assertEqual(("minimal", "standard", "systems", "avionics", "full"), tuple(profile.name for profile in list_profiles()))
self.assertEqual((), get_profile("minimal").datarefs)
self.assertEqual(
    compose_profiles(("standard", "systems", "avionics")),
    get_profile("full").datarefs,
)
```

Assert every path below in exact order, scale `1.0`, no duplicate path, and inability to mutate returned tuples or package-global manifests.

Also assert these exact mandatory capture mappings: longitude → `sim/flightmodel/position/longitude`; latitude → `sim/flightmodel/position/latitude`; altitude MSL feet → `sim/flightmodel/position/elevation` multiplied by `1 / 0.3048`; magnetic heading → `sim/flightmodel/position/mag_psi`; pitch → `sim/flightmodel/position/theta`; roll → `sim/flightmodel/position/phi`.

- [ ] **Step 2: Run tests and confirm profile imports fail**

Run: `uv run python -m unittest tests.test_fdr_profiles -v`

Expected: ERROR because profile APIs are unavailable.

- [ ] **Step 3: Define the exact `standard` manifest**

Use these ordered paths:

```text
sim/cockpit2/gauges/indicators/airspeed_kts_pilot
sim/cockpit2/gauges/indicators/true_airspeed_kts_pilot
sim/cockpit2/gauges/indicators/ground_speed_kt
sim/cockpit2/gauges/indicators/altitude_ft_pilot
sim/cockpit2/gauges/indicators/vvi_fpm_pilot
sim/cockpit2/temperature/outside_air_temp_degc
sim/flightmodel/forces/g_axil
sim/flightmodel/forces/g_nrml
sim/flightmodel/forces/g_side
sim/joystick/yoke_pitch_ratio
sim/joystick/yoke_roll_ratio
sim/joystick/yoke_heading_ratio
sim/cockpit2/controls/flap_ratio
sim/cockpit2/controls/speedbrake_ratio
sim/cockpit2/controls/gear_handle_down
sim/flightmodel2/gear/deploy_ratio[0]
sim/flightmodel2/gear/deploy_ratio[1]
sim/flightmodel2/gear/deploy_ratio[2]
```

- [ ] **Step 4: Define the exact `systems` and `avionics` manifests**

`systems` starts with these paths:

```text
sim/cockpit2/electrical/battery_voltage_indicated_volts[0]
sim/cockpit2/electrical/battery_voltage_indicated_volts[1]
sim/flightmodel/weight/m_fuel[0]
sim/flightmodel/weight/m_fuel[1]
```

Then, for engine index `[0]` followed by `[1]`, append the index to each ordered base:

```text
sim/cockpit2/engine/indicators/fuel_flow_kg_sec
sim/cockpit2/engine/indicators/fuel_pressure_psi
sim/cockpit2/engine/indicators/oil_temperature_deg_C
sim/cockpit2/engine/indicators/oil_pressure_psi
sim/cockpit2/engine/indicators/torque_n_mtr
sim/cockpit2/engine/indicators/prop_speed_rsc
sim/cockpit2/engine/indicators/N1_percent
sim/cockpit2/engine/indicators/N2_percent
sim/cockpit2/engine/indicators/ITT_deg_C
sim/cockpit2/engine/indicators/EGT_deg_C
```

`avionics` is this exact ordered manifest:

```text
sim/cockpit2/gauges/actuators/barometer_setting_in_hg_pilot
sim/cockpit2/autopilot/flight_director_command_bars_pilot
sim/cockpit/autopilot/flight_director_roll
sim/cockpit/autopilot/flight_director_pitch
sim/cockpit/autopilot/autopilot_mode
sim/cockpit2/autopilot/heading_mode
sim/cockpit2/autopilot/altitude_mode
sim/cockpit/autopilot/airspeed
sim/cockpit/autopilot/airspeed_is_mach
sim/cockpit/autopilot/heading_mag
sim/cockpit/autopilot/vertical_velocity
sim/cockpit/autopilot/altitude
sim/cockpit2/radios/actuators/HSI_source_select_pilot
sim/cockpit2/radios/actuators/hsi_obs_deg_mag_pilot
sim/cockpit2/radios/indicators/nav1_hdef_dots_pilot
sim/cockpit2/radios/indicators/nav1_vdef_dots_pilot
sim/cockpit2/radios/actuators/nav1_frequency_hz
sim/cockpit2/radios/actuators/nav2_frequency_hz
sim/cockpit2/radios/actuators/com1_frequency_hz
sim/cockpit2/radios/actuators/com2_frequency_hz
```

- [ ] **Step 5: Implement deterministic composition and run tests**

`full` is computed once as the ordered union of `standard`, `systems`, and `avionics`; it is not a second hand-maintained list. `compose_profiles()` retains the first path position.

```powershell
uv run python -m unittest tests.test_fdr_profiles -v
uv run ruff check xplane_fdr/profiles.py tests/test_fdr_profiles.py
```

- [ ] **Step 6: Commit profiles**

```powershell
git add xplane_fdr tests/test_fdr_profiles.py
git commit -m "feat: add stock x-plane recording profiles"
```

---

### Task 10: Load Strict Adapter-Neutral JSON Configuration

**Files:**
- Create: `xplane_fdr/config.py`
- Create: `xplane_fdr/schemas/__init__.py`
- Create: `xplane_fdr/schemas/fdr-record-config-v1.schema.json`
- Create: `tests/test_fdr_config.py`
- Modify: `xplane_fdr/__init__.py`

**Interfaces:**
- Produces immutable `FDRMetadataConfig`, `FDRDatarefConfig`, and `FDRRecordConfig`.
- Produces `load_record_config(path_or_stream) -> FDRRecordConfig` and `resolve_recording_definition(config) -> FDRRecordingDefinition`.
- Path-opened config streams are owned; caller streams remain open.
- `FDRMetadataConfig` has `aircraft_path: str | None`, `tail_number: str | None`, `local_date: date | None`, `pressure_in_hg: int | float | None`, `isa_offset_c: int | float | None`, `wind_direction_deg: int | float | None`, `wind_speed_kt: int | float | None`, and `comments: tuple[str, ...]`.
- `FDRDatarefConfig` has `path: str`, `scale: int | float | None`, and `comment: str | None`.
- `FDRRecordConfig` has `schema_version: Literal[1]`, `profiles: tuple[str, ...]`, `sampling: FDRSamplingPolicy`, `metadata: FDRMetadataConfig`, `datarefs: tuple[FDRDatarefConfig, ...]`, and `storage: FDRStoragePolicy`.

- [ ] **Step 1: Write failing valid-config and resolution tests**

```python
config = load_record_config(StringIO('{"schema_version":1,"profiles":["standard"],"storage":{"directory":"Output/FDR files"}}'))
definition = resolve_recording_definition(config)
self.assertEqual(0.1, definition.sampling.interval_seconds)
self.assertEqual(Path("Output/FDR files"), definition.storage.directory)
self.assertEqual(get_profile("standard").datarefs, definition.header.datarefs)
```

Cover default `standard`, explicit empty/minimal profile selection, 10 Hz default, optional duration, metadata mapping, custom DataRef order, cross-profile first-position retention, strict unknown properties, schema versions, duplicate paths, booleans, non-finite values, ranges, single-line comments, source/property-path context, and packaged schema availability.

- [ ] **Step 2: Run tests and confirm configuration APIs are missing**

Run: `uv run python -m unittest tests.test_fdr_config -v`

Expected: ERROR because config types and schema are unavailable.

- [ ] **Step 3: Implement explicit standard-library validation**

Use `json.load` and type/range validators; do not perform runtime JSON Schema validation. Reject unknown properties at every object level. `schema_version` is exactly integer `1`; optional `$schema` is a string. Report syntax line/column and semantic paths such as `$.sampling.interval_seconds` and `$.datarefs[2].scale` through `FDRConfigError`.

- [ ] **Step 4: Implement semantic configuration and definition resolution**

Supported sections are `profiles`, `sampling`, `metadata`, `datarefs`, and `storage`. Metadata maps to `ACFT`, `TAIL`, `DATE`, `PRES`, `DISA`, `WIND`, and ordered `COMM`. Custom DataRefs follow composed profiles. An omitted custom scale preserves an earlier declaration or defaults to `1.0`; an omitted comment preserves an earlier comment or remains absent.

- [ ] **Step 5: Implement storage configuration exactly**

`storage.directory` defaults to `Output/FDR files`; `storage.filename` is optional. Reject empty paths, NULs, filename separators, and filenames without a `.fdr` suffix. Do not include connection settings, XPLM callbacks, overwrite permission, or a live output path in this schema.

- [ ] **Step 6: Write the editor schema and verify installed-resource reads**

Set the schema identifier to `https://tvproductions.github.io/xplane-fdr/schemas/fdr-record-config-v1.schema.json`, use `additionalProperties: false` at every object level, and mirror every runtime type/range rule expressible in JSON Schema.

```powershell
uv run python -m unittest tests.test_fdr_config -v
uv run python -c "from importlib.resources import files; import json; json.loads(files('xplane_fdr.schemas').joinpath('fdr-record-config-v1.schema.json').read_text())"
```

- [ ] **Step 7: Commit configuration and schema**

```powershell
git add xplane_fdr tests/test_fdr_config.py
git commit -m "feat: add adapter-neutral recording configuration"
```

---

### Task 11: Export Standards-Conforming GeoJSON

**Files:**
- Create: `xplane_fdr/geojson.py`
- Create: `tests/test_fdr_geojson.py`
- Modify: `xplane_fdr/__init__.py`

**Interfaces:**
- Produces `recording_to_geojson(recording, *, first_utc_date=None) -> dict[str, object]`.

- [ ] **Step 1: Write failing GeoJSON structure and semantics tests**

```python
document = recording_to_geojson(recording)
self.assertEqual("FeatureCollection", document["type"])
point = document["features"][0]
self.assertEqual([sample.longitude, sample.latitude], point["geometry"]["coordinates"])
self.assertNotIn("timestamp_utc", point["properties"])
self.assertEqual(sample.altitude_msl_ft, point["properties"]["altitude_msl_ft"])
```

Cover point-per-sample, no path below two locations, normal `LineString`, antimeridian `MultiLineString` with interpolated boundary latitude, 2D positions, exact 0.3048 MSL conversion, attitudes, DataRef mappings, optional RFC 3339 `Z` timestamps, and strict `json.dumps(document, allow_nan=False)` compatibility.

- [ ] **Step 2: Run tests and confirm the converter is missing**

Run: `uv run python -m unittest tests.test_fdr_geojson -v`

Expected: ERROR because `recording_to_geojson` is unavailable.

- [ ] **Step 3: Port neutral point and timestamp conversion**

Port neutral logic from `xpwebapi/fdr/geojson.py` at `ca7d621`. Return only JSON-compatible built-ins. Resolve rollovers through `FDRRecording.resolved_utc_datetimes()` and never treat local `DATE` as a UTC date.

- [ ] **Step 4: Implement antimeridian-safe path geometry**

When consecutive longitude delta magnitude exceeds 180 degrees, interpolate boundary latitude, close at `+180` or `-180`, and reopen at the opposite boundary. Ensure every child line contains at least two positions.

- [ ] **Step 5: Run tests and strict serialization**

```powershell
uv run python -m unittest tests.test_fdr_geojson -v
uv run python -c "import json; from xplane_fdr import FDRReader, recording_to_geojson; r=FDRReader().read('tests/fixtures/fdr/version4-minimal.fdr'); json.dumps(recording_to_geojson(r), allow_nan=False)"
```

- [ ] **Step 6: Commit GeoJSON conversion**

```powershell
git add xplane_fdr tests/test_fdr_geojson.py
git commit -m "feat: export fdr recordings to geojson"
```

---

### Task 12: Add the Thin Offline Command-Line Interface

**Files:**
- Create: `xplane_fdr/cli.py`
- Create: `tests/test_fdr_cli.py`
- Modify: `pyproject.toml`
- Modify: `uv.lock`

**Interfaces:**
- Adds `xplane-fdr = "xplane_fdr.cli:main"`.
- Adds `inspect`, `validate`, and `to-geojson`; no live-record command.

- [ ] **Step 1: Write failing parser and command tests**

Lock these command shapes:

```text
xplane-fdr validate INPUT
xplane-fdr inspect INPUT [--json] [--first-utc-date YYYY-MM-DD]
xplane-fdr to-geojson INPUT OUTPUT [--first-utc-date YYYY-MM-DD] [--overwrite]
```

Test silent validation success, human and compact sorted JSON inspection, explicit UTC-date rollover, invalid arguments, line-number diagnostics, stderr-only failures, status zero/nonzero, GeoJSON overwrite protection, sibling partial cleanup, and atomic commit.

- [ ] **Step 2: Run tests and confirm CLI imports fail**

Run: `uv run python -m unittest tests.test_fdr_cli -v`

Expected: ERROR because `xplane_fdr.cli` and the console script are absent.

- [ ] **Step 3: Implement argparse and thin handlers**

Handlers call public `FDRReader` and `recording_to_geojson`; do not duplicate parsing or conversion. `validate` writes nothing on success. `inspect --json` writes one LF-terminated document using `allow_nan=False`, sorted keys, and compact separators. Diagnostics are concise and go only to stderr.

- [ ] **Step 4: Implement atomic GeoJSON output**

Validate input and serialize before publishing. Create a unique sibling partial, flush, fsync, close, then link/unlink without overwrite or `os.replace` with overwrite. Convert OS failures to `FDROutputError` and preserve primary-plus-cleanup failure evidence.

- [ ] **Step 5: Add the console script and run CLI/library tests**

```powershell
uv lock
uv sync --frozen
uv run python -m unittest tests.test_fdr_cli tests.test_fdr_reader tests.test_fdr_geojson -v
uv run xplane-fdr --help
```

- [ ] **Step 6: Commit the offline CLI**

```powershell
git add xplane_fdr/cli.py tests/test_fdr_cli.py pyproject.toml uv.lock
git commit -m "feat: add offline fdr commands"
```

---

### Task 13: Publish the Supported API and Documentation

**Files:**
- Modify: `xplane_fdr/__init__.py`
- Modify: `README.md`
- Create: `CHANGELOG.md`
- Create: `BACKLOG.md`
- Create: `mkdocs.yml`
- Create: `docs/index.md`
- Create: `docs/usage/fdr-toolkit.md`
- Create: `docs/reference/fdr.md`
- Create: `tests/test_public_api.py`
- Create: `tests/test_documentation.py`
- Create: `.codex/skills/documentation/SKILL.md`
- Modify: `tests/test_project_skills.py`
- Modify: `HANDOFF.md`

**Interfaces:**
- Produces a deliberate `xplane_fdr.__all__` containing all documented stable imports.
- Documents v3 input/v4 output, stdlib-only runtime, push-first adapters, storage defaults, configuration, GeoJSON, CLI, partial recovery, and XPPython3 installation.

- [ ] **Step 1: Write failing public API and documentation tests**

```python
required = {
    "FDRReader", "FDRWriter", "FDRRecordingSession", "FDRRecordConfig",
    "FDRRecordingProfile", "load_record_config", "recording_to_geojson",
}
self.assertTrue(required.issubset(set(xplane_fdr.__all__)))
for name in required:
    self.assertIsNotNone(getattr(xplane_fdr, name))
```

Documentation tests assert MkDocs navigation, command names, configuration schema link, `Output/FDR files`, generated filename example, MSL/2D explanation, explicit v3 loss warning, no live-record command, XPPython3 wheel guidance, and no claim that capture adapters are bundled.

- [ ] **Step 2: Run tests and confirm docs/API are incomplete**

Run: `uv run python -m unittest tests.test_public_api tests.test_documentation -v`

Expected: FAIL because the stable export set and documentation files are incomplete.

- [ ] **Step 3: Finalize the explicit public surface**

Export public exceptions, models, reader/stream, writer/stream, recording definition/policies/session/protocols, profiles, configuration loader/resolver, and GeoJSON converter. Do not export private renderers, validators, schema internals, or destination helpers.

- [ ] **Step 4: Write user and API documentation**

Include executable examples for reading v3/v4, writing canonical v4, explicit lossy normalization, callback-style `session.record(sample)`, pull convenience, config loading, custom DataRefs, configured storage, GeoJSON, and offline commands. State that XPLM/Web API adapters own capture, cadence scheduling, connections, and plugin lifecycle.

Invoke `writing-skills` and author the documentation skill against this repository's actual MkDocs, API-reference, link-check, and `unittest` documentation-contract commands. Extend `tests/test_project_skills.py` to require the new skill and reject stale `xpwebapi` names.

- [ ] **Step 5: Update handoff state and build docs strictly**

Replace the stale “awaiting written review” handoff with the approved spec commit, implementation plan path, execution workflow choice, and v3 reference-file prerequisite.

```powershell
uv run python -m unittest tests.test_public_api tests.test_documentation -v
uv run mkdocs build --strict
```

- [ ] **Step 6: Commit public documentation**

```powershell
git add xplane_fdr/__init__.py README.md CHANGELOG.md BACKLOG.md mkdocs.yml docs tests/test_public_api.py tests/test_documentation.py HANDOFF.md
git commit -m "docs: publish xplane-fdr library guidance"
```

---

### Task 14: Verify Distribution Artifacts and Release Readiness

**Files:**
- Create: `tools/release.py`
- Create: `tools/installed_smoke.py`
- Create: `tests/test_release_tool.py`
- Create: `tests/test_installed_smoke.py`
- Create: `.codex/skills/release/SKILL.md`
- Modify: `tests/test_project_skills.py`
- Create: `.github/workflows/release.yml`
- Modify: `.github/workflows/ci.yml`
- Modify: `pyproject.toml`
- Modify: `uv.lock`

**Interfaces:**
- Requires one `xplane_fdr-0.1.0-py3-none-any.whl` and one `xplane_fdr-0.1.0.tar.gz`.
- Requires installed artifacts to expose the public API, schema, and `xplane-fdr` commands without importing from the checkout.

- [ ] **Step 1: Write failing archive and installed-smoke tests**

```python
with zipfile.ZipFile(wheel) as archive:
    metadata = archive.read("xplane_fdr-0.1.0.dist-info/METADATA").decode()
    self.assertIn("Requires-Python: >=3.12", metadata)
    self.assertNotIn("Requires-Dist:", metadata)
    self.assertIn("xplane_fdr/schemas/fdr-record-config-v1.schema.json", archive.namelist())
```

Assert exact wheel tag, package modules, one license, schema resource, source-root containment, exclusion of `.codex`, `.git`, `.superpowers`, `docs/superpowers`, caches, and large official fixtures.

- [ ] **Step 2: Run focused tests and confirm release tooling is missing**

Run: `uv run python -m unittest tests.test_release_tool tests.test_installed_smoke -v`

Expected: ERROR because release and installed-smoke modules are unavailable.

- [ ] **Step 3: Implement tag and archive validation**

Adapt the neutral archive mechanics from the source repository. Validate project/runtime version equality, `v<version>` tags, universal wheel naming, empty runtime requirements, required modules/schema/license, and forbidden archive members. Treat unexpected `dist/` files as an error.

Invoke `writing-skills` and author the release skill against the completed release validator, installed smoke script, CI artifact contract, and explicit user authorization gate. Extend `tests/test_project_skills.py` to require it.

- [ ] **Step 4: Implement checkout-independent installed smoke tests**

The script confirms `xplane_fdr.__file__` is outside the checkout, checks every `__all__` name, reads the schema via `importlib.resources`, parses v3/v4 minimal fixtures copied into a temporary directory, writes/read-round-trips canonical v4, and executes interpreter-local `xplane-fdr validate` and `to-geojson`.

- [ ] **Step 5: Run the complete local quality and documentation gates**

```powershell
uv sync --frozen
uv run python -m unittest discover -v
uv run ruff check .
uv run ruff format --check .
uv run ty check
uv run python tools/quality.py check
uv run mkdocs build --strict
```

Expected: every command exits zero. Do not substitute another test runner.

- [ ] **Step 6: Build and validate immutable artifacts**

Prepare a clean `dist/`, then run:

```powershell
uv build --no-sources
uv tool run twine check --strict dist/*
uv run python tools/release.py check-dist dist
```

Expected: one universal wheel, one sdist, strict metadata success, and no runtime dependency declaration.

- [ ] **Step 7: Smoke-test the wheel on Python 3.12, 3.13, and 3.14**

Create isolated environments outside the source checkout, install the exact wheel, and run `tools/installed_smoke.py 0.1.0` with each interpreter. Confirm the command resolves from each environment's scripts directory.

- [ ] **Step 8: Review forbidden scope and request code review**

Search tracked source for unresolved placeholders, adapter imports, network libraries, XPLM imports, non-stdlib runtime requirements, a live-record CLI, copied full Laminar fixtures, and GPL-derived code. Resolve every unexpected hit. Invoke `requesting-code-review` and address findings before release authorization.

- [ ] **Step 9: Commit release verification**

```powershell
git add tools tests/test_release_tool.py tests/test_installed_smoke.py .github/workflows pyproject.toml uv.lock
git commit -m "build: verify xplane-fdr release artifacts"
```

- [ ] **Step 10: Stop at the release-authorization gate**

Re-run Steps 5–7 after the final commit and report exact artifact names and hashes. Do not push, tag `v0.1.0`, publish to PyPI, or create a GitHub release until the user explicitly authorizes those external actions.

---

## Completion Criteria

- `xplane-fdr` installs from a `py3-none-any` wheel on Python 3.12, 3.13, and 3.14 with no runtime dependencies.
- Verified v3 and v4 fixtures parse incrementally; v3 positional fields are retained and lossy normalization is explicit.
- Canonical v4 output is deterministic, round-trips, and starts with exact bytes `A\n4\n`.
- A callback can call `FDRRecordingSession.record(sample)` directly without threads, sleeps, polling, networking, or simulator imports.
- Configured storage follows complete-path, caller-filename, configured-filename, generated-filename precedence and defaults to XP12-relative `Output/FDR files`.
- Stock profiles and strict JSON configuration are immutable, ordered, adapter-neutral, and schema-backed without a runtime schema dependency.
- GeoJSON uses 2D longitude/latitude geometry, explicit MSL properties, optional caller-resolved UTC timestamps, and antimeridian splitting.
- `xplane-fdr inspect|validate|to-geojson` obeys exit, stream, atomic-output, and overwrite contracts; there is no live-record command.
- Full `unittest` discovery, quality, strict docs, artifact inspection, and installed-wheel smoke checks pass.
- The branch is code-reviewed and stops before any push, tag, publication, or GitHub release.
