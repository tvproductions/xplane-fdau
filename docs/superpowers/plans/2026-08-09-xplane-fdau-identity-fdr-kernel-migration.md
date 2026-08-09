# xplane-fdau Identity and Native FDR Kernel Migration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Transform the unreleased `xplane-fdr` project into the unreleased `xplane-fdau` distribution while preserving the reviewed native X-Plane FDR kernel beneath explicit format and sink boundaries.

**Architecture:** The root `xplane_fdau` package owns only distribution identity in this increment. Native parsing, models, writing, profiles, configuration, GeoJSON, and immutable recording definitions live under `xplane_fdau.formats.xplane_fdr`; the push-first publication lifecycle lives under `xplane_fdau.sinks.xplane_fdr`. Existing behavior moves without compatibility shims, while packaging, CLI, documentation, release validation, and installed-wheel checks adopt the new identity.

**Tech Stack:** Python 3.12+, standard library at runtime, `unittest`, uv, Ruff, ty, coverage, Bandit, detect-secrets, Interrogate, Vulture, Xenon, MkDocs, Twine, GitHub Actions.

## Global Constraints

- Read `HANDOFF.md`, `docs/architecture/xplane12_virtual_fdau_ecosystem_design.md`, and `docs/superpowers/specs/2026-08-09-xplane-fdau-identity-fdr-kernel-migration-design.md` before changing the project.
- Use Python 3.12 or newer and declare `dependencies = []`.
- Use `unittest` only; pytest is prohibited.
- Every runtime module may import only the Python standard library or another `xplane_fdau` module.
- Do not import xpwebapi, XPPython3, `xp`, XPLM, q4xpcc, or any network client.
- Do not add generic FDAU contract shells, adapters, ARINC behavior, FDM, or FOQA behavior in this increment.
- Do not ship `xplane_fdr`, an `xplane-fdr` console alias, or old schema URLs.
- Preserve native FDR v3/v4 behavior, explicit lossy normalization, deterministic v4 output, and the approved publication commit-point contract.
- Preserve imported architecture documents byte-for-byte and retain their q4xpcc provenance hashes.
- Do not push, tag, publish to PyPI, create a GitHub release, or enable a publishing workflow.
- Do not remove or move a linked worktree until its branch is clean, durable, reviewed, and integrated.

---

## Current state and target files

Execution starts on `feature/xplane-fdr-core` in the existing linked worktree. The branch contains the reviewed native FDR kernel plus design commits `5135502` and `bff0388`. The shared Git remote still uses the old URL and must be updated in Task 1.

Target runtime responsibilities:

```text
xplane_fdau/__init__.py                         distribution version only
xplane_fdau/py.typed                            PEP 561 marker for the full distribution
xplane_fdau/cli.py                              top-level command with an `fdr` command group
xplane_fdau/formats/__init__.py                 formats namespace marker
xplane_fdau/formats/xplane_fdr/__init__.py      supported native-format imports
xplane_fdau/formats/xplane_fdr/errors.py        native parse/config/output errors
xplane_fdau/formats/xplane_fdr/models.py        immutable native FDR values
xplane_fdau/formats/xplane_fdr/reader.py        incremental v3/v4 parser
xplane_fdau/formats/xplane_fdr/writer.py        deterministic canonical-v4 serializer
xplane_fdau/formats/xplane_fdr/profiles.py      native FDR projection profiles
xplane_fdau/formats/xplane_fdr/definition.py    sampling/storage/recording definitions
xplane_fdau/formats/xplane_fdr/config.py        strict native FDR configuration
xplane_fdau/formats/xplane_fdr/geojson.py       native recording to GeoJSON projection
xplane_fdau/formats/xplane_fdr/schemas/         packaged native configuration schema
xplane_fdau/sinks/__init__.py                   sinks namespace marker
xplane_fdau/sinks/xplane_fdr.py                 push-first native FDR publication lifecycle
```

The current tests keep their descriptive `test_fdr_*` filenames. Imports and identity assertions change; behavioral assertions do not weaken.

### Task 1: Rename the distribution and relocate the native package atomically

**Files:**
- Create: `xplane_fdau/__init__.py`
- Create: `xplane_fdau/formats/__init__.py`
- Create: `xplane_fdau/formats/xplane_fdr/__init__.py`
- Move: `xplane_fdr/errors.py` → `xplane_fdau/formats/xplane_fdr/errors.py`
- Move: `xplane_fdr/models.py` → `xplane_fdau/formats/xplane_fdr/models.py`
- Move: `xplane_fdr/reader.py` → `xplane_fdau/formats/xplane_fdr/reader.py`
- Move: `xplane_fdr/writer.py` → `xplane_fdau/formats/xplane_fdr/writer.py`
- Move: `xplane_fdr/profiles.py` → `xplane_fdau/formats/xplane_fdr/profiles.py`
- Move: `xplane_fdr/config.py` → `xplane_fdau/formats/xplane_fdr/config.py`
- Move: `xplane_fdr/geojson.py` → `xplane_fdau/formats/xplane_fdr/geojson.py`
- Move: `xplane_fdr/recording.py` → `xplane_fdau/formats/xplane_fdr/recording.py` temporarily; Task 2 splits it
- Move: `xplane_fdr/schemas/` → `xplane_fdau/formats/xplane_fdr/schemas/`
- Move and edit: `xplane_fdr/cli.py` → `xplane_fdau/cli.py`
- Move: `xplane_fdr/py.typed` → `xplane_fdau/py.typed`
- Delete after moves: `xplane_fdr/__init__.py`
- Modify: `pyproject.toml`
- Modify mechanically: every `tests/test_*.py` import of `xplane_fdr`
- Test: `tests/test_project_metadata.py`
- Test: `tests/test_public_api.py`

**Interfaces:**
- Consumes: the existing public native FDR names and version `0.1.0`.
- Produces: `xplane_fdau.__version__ == "0.1.0"` and the temporarily complete native API at `xplane_fdau.formats.xplane_fdr`.

- [ ] **Step 1: Record preflight state and update the shared remote**

Run:

```powershell
git status --short
git branch --show-current
git worktree list --porcelain
git tag --list
git remote -v
gh repo view tvproductions/xplane-fdau --json name,url,isPrivate,isArchived,latestRelease,issues,pullRequests
git remote set-url origin https://github.com/tvproductions/xplane-fdau.git
git remote get-url origin
```

Expected: the worktree is clean, the branch is `feature/xplane-fdr-core`, no tag or release exists, and the final remote output is exactly `https://github.com/tvproductions/xplane-fdau.git`. Do not push.

- [ ] **Step 2: Write failing identity and import-boundary tests**

Replace `tests/test_project_metadata.py` with assertions equivalent to:

```python
from pathlib import Path
import importlib.util
import tomllib
import unittest


class ProjectMetadataTests(unittest.TestCase):
    def test_distribution_contract_is_dependency_free_fdau(self) -> None:
        project = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))["project"]
        self.assertEqual("xplane-fdau", project["name"])
        self.assertEqual("0.1.0", project["version"])
        self.assertEqual(">=3.12", project["requires-python"])
        self.assertEqual([], project["dependencies"])
        self.assertEqual({"xplane-fdau": "xplane_fdau.cli:main"}, project["scripts"])

    def test_runtime_root_exposes_only_matching_version(self) -> None:
        import xplane_fdau

        self.assertEqual("0.1.0", xplane_fdau.__version__)
        self.assertEqual(["__version__"], xplane_fdau.__all__)

    def test_unreleased_legacy_namespace_is_absent(self) -> None:
        self.assertIsNone(importlib.util.find_spec("xplane_fdr"))
```

Change `tests/test_public_api.py` to import `xplane_fdau.formats.xplane_fdr as native_fdr` and assert the existing native names against `native_fdr.__all__`; Task 2 will separate sink names.

- [ ] **Step 3: Run the identity tests to prove RED**

Run:

```powershell
uv run python -m unittest tests.test_project_metadata tests.test_public_api -v
```

Expected: import and metadata failures because `xplane_fdau` and `xplane-fdau` do not exist yet.

- [ ] **Step 4: Move the source with Git and create the new root**

Use `git mv` for every tracked source so history is retained. Create the namespace files with these exact root contracts:

```python
# xplane_fdau/__init__.py
"""Virtual Flight Data Acquisition Unit / Flight Data Interface Unit for X-Plane."""

__all__ = ["__version__"]
__version__ = "0.1.0"
```

```python
# xplane_fdau/formats/__init__.py
"""Host-neutral flight-data formats."""
```

Move the former root export surface into `xplane_fdau/formats/xplane_fdr/__init__.py`, remove `__version__` from its `__all__`, and remove its local version assignment. Update `xplane_fdau/cli.py` to use absolute imports from `xplane_fdau.formats.xplane_fdr` while preserving command behavior for now.

- [ ] **Step 5: Change project metadata and mechanical imports**

Set the exact active metadata in `pyproject.toml`:

```toml
[project]
name = "xplane-fdau"
version = "0.1.0"
description = "Standard-library-only Python toolkit for acquiring, normalizing, recording, replaying, and distributing X-Plane flight data, including native FDR v3/v4 support."
requires-python = ">=3.12"
dependencies = []

[project.scripts]
xplane-fdau = "xplane_fdau.cli:main"

[project.urls]
Homepage = "https://tvproductions.github.io/xplane-fdau/"
Documentation = "https://tvproductions.github.io/xplane-fdau/"
Issues = "https://github.com/tvproductions/xplane-fdau/issues"
Repository = "https://github.com/tvproductions/xplane-fdau"

[tool.coverage.run]
source = ["xplane_fdau"]
```

Update test imports mechanically from `xplane_fdr` to `xplane_fdau.formats.xplane_fdr`; import the root version only from `xplane_fdau`. Run `uv lock` so the lockfile records the renamed local project without changing dependency intent.

- [ ] **Step 6: Run focused and complete tests**

Run:

```powershell
uv run python -m unittest tests.test_project_metadata tests.test_public_api -v
uv run python -m unittest discover -v
uv run ruff check xplane_fdau tests tools
uv run ruff format --check xplane_fdau tests tools
uv run ty check
```

Expected: all commands exit zero. At this checkpoint, the native recording implementation may still reside temporarily at `formats.xplane_fdr.recording`; no legacy top-level package remains.

- [ ] **Step 7: Commit the atomic identity move**

```powershell
git add pyproject.toml uv.lock xplane_fdau tests
git commit -m "refactor: rename package to xplane-fdau"
```

### Task 2: Establish the format-definition and sink boundary

**Files:**
- Create: `xplane_fdau/formats/xplane_fdr/definition.py`
- Create: `xplane_fdau/sinks/__init__.py`
- Create: `xplane_fdau/sinks/xplane_fdr.py`
- Delete: `xplane_fdau/formats/xplane_fdr/recording.py`
- Modify: `xplane_fdau/formats/xplane_fdr/config.py`
- Modify: `xplane_fdau/formats/xplane_fdr/__init__.py`
- Test: `tests/test_public_api.py`
- Test: `tests/test_fdr_config.py`
- Test: `tests/test_fdr_recording.py`
- Test: `tests/test_fdr_writer.py`

**Interfaces:**
- Consumes: native `FDRHeader`, `FDRSample`, `FDRWriter`, `FDRStreamWriter`, and existing recording behavior.
- Produces: immutable definitions in `formats.xplane_fdr.definition`, native-format exports in `formats.xplane_fdr`, and the public sink API in `sinks.xplane_fdr`.

- [ ] **Step 1: Write failing public-boundary tests**

Make `tests/test_public_api.py` assert these exact ownership sets:

```python
import xplane_fdau
import xplane_fdau.formats.xplane_fdr as native_fdr
import xplane_fdau.sinks.xplane_fdr as native_sink

FORMAT_NAMES = {
    "FDRConfigError", "FDRDataref", "FDRDatarefConfig", "FDRError",
    "FDRHeader", "FDRLegacyColumn", "FDRMetadata", "FDRMetadataConfig",
    "FDRNormalizationResult", "FDROutputError", "FDRParseError",
    "FDRRecordConfig", "FDRReader", "FDRRecording", "FDRRecordingProfile",
    "FDRRecordingStateError", "FDRSample", "FDRSampleStream",
    "FDRStreamWriter", "FDRTrajectorySource", "FDRValidationError", "FDRWriter",
    "compose_profiles", "get_profile", "list_profiles", "load_record_config",
    "mandatory_trajectory_sources", "recording_to_geojson",
    "resolve_recording_definition",
}
SINK_NAMES = {
    "FDRRecordingDefinition", "FDRRecordingSession", "FDRSampleSink",
    "FDRSampleSource", "FDRSamplingPolicy", "FDRStoragePolicy",
}

self.assertEqual(["__version__"], xplane_fdau.__all__)
self.assertEqual(FORMAT_NAMES, set(native_fdr.__all__))
self.assertEqual(SINK_NAMES, set(native_sink.__all__))
```

Update recording tests to import session and policy names from `xplane_fdau.sinks.xplane_fdr`. Keep model, reader, writer, and error imports in the format package.

- [ ] **Step 2: Run focused tests to prove RED**

Run:

```powershell
uv run python -m unittest tests.test_public_api tests.test_fdr_config tests.test_fdr_recording tests.test_fdr_writer -v
```

Expected: failures because `xplane_fdau.sinks.xplane_fdr` and the separated export surfaces do not exist.

- [ ] **Step 3: Split definitions from the publication lifecycle**

Move `utc_now`, `_positive_finite_float`, `_fdr_basename`, `_utc_instant`,
`FDRSamplingPolicy`, `FDRStoragePolicy`, `FDRRecordingDefinition`, and
`_resolved_destination` into `formats/xplane_fdr/definition.py` without
changing their bodies or signatures. In particular, retain these exact public
fields and the current destination-resolution behavior:

```python
def utc_now() -> datetime:
    return datetime.now(UTC)

@dataclass(frozen=True, slots=True)
class FDRSamplingPolicy:
    interval_seconds: float = 0.1
    duration_seconds: float | None = None

@dataclass(frozen=True, slots=True)
class FDRStoragePolicy:
    directory: Path = Path("Output/FDR files")
    filename: str | None = None

@dataclass(frozen=True, slots=True)
class FDRRecordingDefinition:
    header: FDRHeader
    sampling: FDRSamplingPolicy
    storage: FDRStoragePolicy

def _resolved_destination(
    definition: FDRRecordingDefinition,
    *,
    xplane_root: str | os.PathLike[str] | None,
    filename: str | None,
    started_at_utc: datetime | None,
    utc_clock: Callable[[], datetime],
) -> Path:
    directory = definition.storage.directory
    if not directory.is_absolute():
        if xplane_root is None:
            raise FDRValidationError("relative storage directory requires xplane_root")
        directory = Path(xplane_root) / directory

    if filename is not None:
        resolved_filename = _fdr_basename(filename, "filename")
    elif definition.storage.filename is not None:
        resolved_filename = definition.storage.filename
    else:
        instant = started_at_utc if started_at_utc is not None else utc_clock()
        started = _utc_instant(instant, "recording start")
        resolved_filename = f"xplane-fdr-{started:%Y%m%dT%H%M%S}{started.microsecond:06d}Z.fdr"
    return directory / resolved_filename
```

Move `FDRSampleSource`, `FDRSampleSink`, and `FDRRecordingSession` into `sinks/xplane_fdr.py`. Import the definitions and `_resolved_destination` from the format definition module, and re-export the six exact `SINK_NAMES`. Update `config.py` to import definitions from `.definition`, never from the sink.

- [ ] **Step 4: Make dependency direction executable**

Add a test that parses runtime imports with `ast` and fails if any file below `xplane_fdau/formats` imports `xplane_fdau.sinks` or uses a relative import that resolves into sinks. Assert that `sinks/xplane_fdr.py` imports only standard-library modules and `xplane_fdau.formats.xplane_fdr` modules.

- [ ] **Step 5: Run focused and complete verification**

Run:

```powershell
uv run python -m unittest tests.test_public_api tests.test_fdr_config tests.test_fdr_recording tests.test_fdr_writer -v
uv run python -m unittest discover -v
uv run ruff check xplane_fdau tests
uv run ruff format --check xplane_fdau tests
uv run ty check
```

Expected: all commands exit zero and no `formats → sinks` dependency exists.

- [ ] **Step 6: Commit the semantic split**

```powershell
git add xplane_fdau tests
git commit -m "refactor: separate native fdr format and sink"
```

### Task 3: Nest native FDR commands beneath `xplane-fdau fdr`

**Files:**
- Modify: `xplane_fdau/cli.py`
- Modify: `tests/test_fdr_cli.py`
- Modify: `tests/test_installed_smoke.py`

**Interfaces:**
- Consumes: `FDRReader`, `recording_to_geojson`, `FDRError`, and the existing atomic JSON output helpers.
- Produces: `build_parser() -> argparse.ArgumentParser` and `main(argv: list[str] | None = None) -> int` with an explicit `fdr` command group.

- [ ] **Step 1: Change CLI tests to the approved command grammar**

Use argument vectors shaped exactly like:

```python
["fdr", "validate", str(input_path)]
["fdr", "inspect", str(input_path), "--json", "--first-utc-date", "2026-08-07"]
["fdr", "to-geojson", str(input_path), str(output_path), "--overwrite"]
```

Assert:

```python
self.assertEqual("fdr", parsed.domain)
self.assertEqual("validate", parsed.command)
```

Also assert the former flat `validate`, `inspect`, and `to-geojson` shapes return status 2; `xplane-fdau --help` lists `fdr`, while `xplane-fdau fdr --help` lists exactly the three offline native commands.

- [ ] **Step 2: Run CLI tests to prove RED**

Run:

```powershell
uv run python -m unittest tests.test_fdr_cli -v
```

Expected: parser failures because the current commands are flat and the program name is still old inside the parser.

- [ ] **Step 3: Implement the nested parser without duplicating handlers**

Build the parser with this structure:

```python
parser = _ArgumentParser(prog="xplane-fdau", description="Virtual FDAU/FDIU tools for X-Plane")
domains = parser.add_subparsers(dest="domain", required=True)
fdr = domains.add_parser("fdr", help="native X-Plane FDR tools")
commands = fdr.add_subparsers(dest="command", required=True)
```

Attach the existing arguments to the three parsers created from `commands`. Keep `main()` dispatching on `arguments.command`; no new handler or live command is introduced.

- [ ] **Step 4: Run focused and complete tests**

Run:

```powershell
uv run python -m unittest tests.test_fdr_cli tests.test_installed_smoke -v
uv run python -m unittest discover -v
```

Expected: all commands exit zero.

- [ ] **Step 5: Commit the CLI namespace**

```powershell
git add xplane_fdau/cli.py tests/test_fdr_cli.py tests/test_installed_smoke.py
git commit -m "feat: namespace native fdr commands"
```

### Task 4: Replace active project documentation and schema identity

**Files:**
- Modify: `README.md`
- Modify: `mkdocs.yml`
- Move: `docs/usage/fdr-toolkit.md` → `docs/usage/native-fdr.md`
- Move: `docs/reference/fdr.md` → `docs/reference/native-fdr.md`
- Modify: `docs/index.md`
- Modify: `docs/schemas/fdr-record-config-v1.schema.json`
- Modify: `xplane_fdau/formats/xplane_fdr/schemas/fdr-record-config-v1.schema.json`
- Modify: `AGENTS.md`
- Modify: `BACKLOG.md`
- Modify: `CHANGELOG.md`
- Modify: `HANDOFF.md`
- Modify: `.codex/skills/code-quality/SKILL.md`
- Modify: `.codex/skills/documentation/SKILL.md`
- Modify: `.codex/skills/git-sync/SKILL.md`
- Modify: `.codex/skills/hygiene/SKILL.md`
- Modify: `.codex/skills/release/SKILL.md`
- Test: `tests/test_documentation.py`
- Test: `tests/test_project_skills.py`

**Interfaces:**
- Consumes: the copied architecture documents, new import paths, nested CLI, and native FDR behavior.
- Produces: active user and contributor guidance that consistently identifies FDAU as the product and native `.fdr` as one lossy format/sink.

- [ ] **Step 1: Write failing documentation and provenance contracts**

Update `tests/test_documentation.py` to require these active strings:

```python
required = (
    "xplane-fdau",
    "xplane_fdau.formats.xplane_fdr",
    "xplane_fdau.sinks.xplane_fdr",
    "xplane-fdau fdr inspect",
    "xplane-fdau fdr validate",
    "xplane-fdau fdr to-geojson",
    "lossy projection",
    "canonical FDAU archive",
    "standard library",
)
```

Assert the two imported architecture files have these exact SHA-256 values:

```python
{
    "xplane12_virtual_fdau_ecosystem_design.md": "fc0fe7c0c6c37e51f52dec2781ce840dec729365754f9afce3b308306ae54480",
    "xplane12_foqa_fdr_addon_design_spec_v2.md": "9333d74bdb2ffeb9a8d21fdf508393289bf1e230f775f55cd36a5ae01dbd23ad",
}
```

Restrict old-identity rejection to active surfaces—README, MkDocs, project metadata, workflows, current guides, current API reference, tools, and project skills—because historical and imported architecture documents intentionally discuss `xplane-fdr`.

- [ ] **Step 2: Run documentation tests to prove RED**

Run:

```powershell
uv run python -m unittest tests.test_documentation tests.test_project_skills -v
```

Expected: failures for old site, imports, commands, guide paths, schema URL, handoff, and skill descriptions.

- [ ] **Step 3: Rewrite active documentation around the approved boundary**

Use this opening contract in README and the documentation index:

```markdown
`xplane-fdau` is a standard-library-only virtual Flight Data Acquisition Unit /
Flight Data Interface Unit toolkit for X-Plane. Native X-Plane FDR v3/v4 is
retained as one deliberately lossy replay format and recording sink; it is not
the canonical FDAU archive.
```

Document the nested imports and commands exactly. State that version `0.1.0` is unreleased and remove installation language that implies availability on PyPI. Keep operational native FDR guidance for v3/v4, normalization, output storage, GeoJSON, XPPython3 compatibility, and publication recovery.

- [ ] **Step 4: Update schemas and project instructions**

Set both schema copies to:

```json
{
  "$id": "https://tvproductions.github.io/xplane-fdau/schemas/fdr-record-config-v1.schema.json",
  "title": "xplane-fdau native X-Plane FDR recording configuration version 1"
}
```

Preserve every other schema constraint and byte equality between packaged and published copies. Update `AGENTS.md` and `HANDOFF.md` to name the parent architecture, approved migration spec, and current plan. State that the next release remains prohibited until the canonical vertical slice is complete.

- [ ] **Step 5: Update project-local skills**

Replace active `xplane-fdr` identity text with `xplane-fdau`, update paths and artifact names, keep `unittest` and standard-library boundaries, and make the release skill stop after local readiness because publication is not authorized for this increment.

- [ ] **Step 6: Validate documentation and commit**

Run:

```powershell
uv run python -m unittest tests.test_documentation tests.test_project_skills -v
uv run mkdocs build --strict
git diff --check
```

Expected: all commands exit zero and imported architecture hashes are unchanged.

```powershell
git add README.md mkdocs.yml docs AGENTS.md BACKLOG.md CHANGELOG.md HANDOFF.md .codex/skills tests/test_documentation.py tests/test_project_skills.py xplane_fdau/formats/xplane_fdr/schemas
git commit -m "docs: publish xplane-fdau identity"
```

### Task 5: Harden non-publishing build, CI, and installed-artifact checks

**Files:**
- Modify: `tools/release.py`
- Modify: `tools/installed_smoke.py`
- Modify: `tools/quality.py`
- Modify: `tests/test_release_tool.py`
- Modify: `tests/test_installed_smoke.py`
- Modify: `tests/test_release_workflows.py`
- Modify: `tests/test_quality_tool.py`
- Modify: `.github/workflows/ci.yml`
- Move and replace: `.github/workflows/release.yml` → `.github/workflows/release-readiness.yml`
- Modify: `.pre-commit-config.yaml`
- Modify: `.secrets.baseline` only if path relocation changes tracked findings after deliberate review

**Interfaces:**
- Consumes: distribution `xplane-fdau`, package `xplane_fdau`, console script `xplane-fdau`, version `0.1.0`.
- Produces: strict local artifact validation and manual non-publishing release readiness for one immutable artifact pair.

- [ ] **Step 1: Write failing artifact and workflow tests**

Set test constants and synthetic archive roots to:

```python
PACKAGE = "xplane_fdau"
PROJECT = "xplane-fdau"
WHEEL = "xplane_fdau-0.1.0-py3-none-any.whl"
SDIST = "xplane_fdau-0.1.0.tar.gz"
```

Update workflow tests to require:

```python
self.assertIn("workflow_dispatch:", readiness)
self.assertNotIn("uv publish", readiness)
self.assertNotIn("id-token: write", readiness)
self.assertNotIn("tags:", readiness)
self.assertNotIn("publish-pypi:", readiness)
```

Installed-smoke tests must require `xplane_fdau`, reject an installed `xplane_fdr`, resolve `xplane-fdau` beside the interpreter, load the nested schema resource, and invoke `fdr validate` and `fdr to-geojson`.

- [ ] **Step 2: Run release-focused tests to prove RED**

Run:

```powershell
uv run python -m unittest tests.test_release_tool tests.test_installed_smoke tests.test_release_workflows tests.test_quality_tool -v
```

Expected: failures for old package, archive, console, workflow, and quality paths.

- [ ] **Step 3: Update local validators and installed smoke**

In `tools/release.py`, use:

```python
PACKAGE = "xplane_fdau"
PROJECT = "xplane-fdau"
RELEASE_VERSION = "0.1.0"
```

Remove `validate_tag` and the `check-tag` subcommand because this increment cannot create a release tag. Keep exact metadata parsing, universal-wheel tag checks, normalized archive containment, exact source-byte checks, one-license checks, and forbidden-member checks.

In `tools/installed_smoke.py`, import:

```python
import xplane_fdau
import xplane_fdau.formats.xplane_fdr as native_fdr
```

Load the schema through `importlib.resources.files("xplane_fdau.formats.xplane_fdr")`, run native round trips through `native_fdr`, and call the console script with the `fdr` prefix.

- [ ] **Step 4: Replace live release automation with manual readiness**

Rename the workflow and use only:

```yaml
name: release-readiness

on:
  workflow_dispatch:

permissions:
  contents: read
```

Keep validation, exact artifact upload/download, and the Python 3.12–3.14 installed-wheel matrix. Delete every tag trigger, protected publishing environment, OIDC permission, and publish command. Update CI artifact paths and temporary environment names to `xplane-fdau`.

- [ ] **Step 5: Update quality and pre-commit paths**

Set `SOURCE_PATHS = ("xplane_fdau", "tests", "tools")`, Bandit and complexity targets to `xplane_fdau`, and coverage source to the new root. Preserve the configured gate order and thresholds.

- [ ] **Step 6: Run focused tests and build the renamed artifacts**

Run:

```powershell
uv run python -m unittest tests.test_release_tool tests.test_installed_smoke tests.test_release_workflows tests.test_quality_tool -v
$taskArtifactDir = Join-Path ([System.IO.Path]::GetTempPath()) ("xplane-fdau-task5-" + [guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Path $taskArtifactDir | Out-Null
uv build --no-sources --out-dir $taskArtifactDir
uv tool run twine check --strict "$taskArtifactDir\xplane_fdau-0.1.0-py3-none-any.whl" "$taskArtifactDir\xplane_fdau-0.1.0.tar.gz"
uv run python tools/release.py check-dist $taskArtifactDir
```

Expected: all commands exit zero; the fresh temporary directory contains no old artifact.

- [ ] **Step 7: Commit build and workflow migration**

```powershell
git add tools tests .github .pre-commit-config.yaml .secrets.baseline
git commit -m "build: validate unreleased xplane-fdau artifacts"
```

### Task 6: Reduce reader header complexity without changing behavior

**Files:**
- Modify: `xplane_fdau/formats/xplane_fdr/reader.py`
- Modify: `tests/test_fdr_reader.py`

**Interfaces:**
- Consumes: `FDRSampleStream._parse_header() -> FDRHeader` and all existing parse/error contracts.
- Produces: the same method contract with every Xenon block at rank C or better.

- [ ] **Step 1: Use systematic debugging to establish the exact failure**

Run:

```powershell
uv run python -m unittest tests.test_fdr_reader -v
uv run python tools/quality.py complexity
```

Expected: reader tests pass, while complexity exits nonzero and identifies `_parse_header` as rank D against maximum C. Record this as the RED gate; do not lower the threshold.

- [ ] **Step 2: Strengthen behavior characterization before refactoring**

Add one table-driven test that feeds headers containing ordered blank lines, comments, metadata, DATE, v3 TIME, v3 legacy DREF metadata, v4 DREF declarations, the first sample boundary, and malformed records. Assert the same header values, first sample, and source line in each failure. Run it once and confirm it passes before refactoring; it protects behavior while the already-failing complexity command supplies RED.

- [ ] **Step 3: Extract marker and header-record responsibilities**

Introduce a private accumulator:

```python
@dataclass(slots=True)
class _HeaderState:
    comments: list[str] = field(default_factory=list)
    metadata: list[FDRMetadata] = field(default_factory=list)
    datarefs: list[FDRDataref] = field(default_factory=list)
    local_date: date | None = None
    last_line: int = 0
```

Extract narrowly typed helpers with the following implementations; this is a
decomposition of the existing branches, not a grammar change:

```python
def _parse_origin(self) -> str:
    line, text = self._next_nonblank("missing origin marker")
    origin = text.strip()
    if origin not in {"A", "I"}:
        self._parse_error(line, "origin marker must be 'A' or 'I'")
    return origin

def _parse_version(self) -> tuple[int, int]:
    line, text = self._next_nonblank("missing version line")
    match = _VERSION_PATTERN.fullmatch(text.strip())
    if match is None:
        self._parse_error(line, "version line must begin with an integer and optional suffix text")
    try:
        version = int(match.group(1))
    except ValueError as error:
        self._parse_error(line, f"invalid version integer: {error}")
    if version not in {3, 4}:
        self._parse_error(line, "reader supports versions 3 and 4 only")
    return line, version

def _collect_header(self, version: int, origin: str, state: _HeaderState) -> None:
    for line, text in self._lines:
        stripped = text.strip()
        if not stripped:
            continue
        kind, separator, payload = stripped.partition(",")
        kind = kind.strip()
        if (version == 3 and kind == "DATA") or (version == 4 and ":" in kind):
            self._first_sample = (line, stripped)
            return
        if not separator:
            self._parse_error(line, "header record requires a comma")
        state.last_line = line
        self._append_header_record(version, origin, state, line, kind, payload.strip())

def _append_header_record(
    self, version: int, origin: str, state: _HeaderState, line: int, kind: str, payload: str
) -> None:
    if kind == "COMM":
        state.comments.append(payload)
        return
    if kind == "DREF" and version == 4:
        dataref = self._parse_dataref(payload, line)
        self._validate_dataref_append(
            origin, state.comments, state.metadata, state.datarefs, dataref, state.local_date, line
        )
        state.datarefs.append(dataref)
        return
    if _METADATA_PATTERN.fullmatch(kind):
        state.metadata.append(self._validated(FDRMetadata, line, kind, payload))
        if kind == "DATE":
            state.local_date = self._parse_date(payload, line)
        elif kind == "TIME" and version == 3:
            self._v3_start_time = self._parse_time(payload, line, name="TIME")
        return
    self._parse_error(line, "metadata key must be four-character uppercase text")

def _build_header(self, version: int, origin: str, state: _HeaderState) -> FDRHeader:
    if version == 3 and self._v3_start_time is None:
        required_line = self._first_sample[0] if self._first_sample is not None else state.last_line
        self._parse_error(required_line, "version 3 requires a valid TIME header")
    return self._validated(
        FDRHeader,
        state.last_line,
        source_version=version,
        source_origin=origin,
        comments=tuple(state.comments),
        metadata=tuple(state.metadata),
        datarefs=tuple(state.datarefs) if version == 4 else (),
        legacy_columns=_VERSION_3_LEGACY_COLUMNS if version == 3 else (),
        local_date=state.local_date,
    )
```

`_parse_header` becomes this straight-line orchestration:

```python
def _parse_header(self) -> FDRHeader:
    origin = self._parse_origin()
    version_line, version = self._parse_version()
    state = _HeaderState(last_line=version_line)
    self._collect_header(version, origin, state)
    return self._build_header(version, origin, state)
```

`_collect_header` owns iteration and sample-boundary detection;
`_append_header_record` owns COMM/DREF/metadata dispatch; `_build_header` owns
the v3 TIME requirement and final validation. Preserve the lexical version and
error translation behavior exactly.

- [ ] **Step 4: Run behavior, static, and complexity gates**

Run:

```powershell
uv run python -m unittest tests.test_fdr_reader -v
uv run ruff check xplane_fdau/formats/xplane_fdr/reader.py tests/test_fdr_reader.py
uv run ruff format --check xplane_fdau/formats/xplane_fdr/reader.py tests/test_fdr_reader.py
uv run ty check
uv run python tools/quality.py complexity
```

Expected: every command exits zero and Xenon reports no block worse than C.

- [ ] **Step 5: Commit the behavior-preserving decomposition**

```powershell
git add xplane_fdau/formats/xplane_fdr/reader.py tests/test_fdr_reader.py
git commit -m "refactor: decompose native fdr header parsing"
```

### Task 7: Close the migration contract and perform final verification

**Files:**
- Modify: `HANDOFF.md`
- Modify: `CHANGELOG.md`
- Modify: `BACKLOG.md`
- Test: `tests/test_project_metadata.py`
- Test: `tests/test_documentation.py`

**Interfaces:**
- Consumes: the completed renamed source tree, native format/sink boundaries, nested CLI, documentation, and non-publishing artifact workflow.
- Produces: a clean, reviewed, unreleased migration checkpoint ready for integration and the next canonical-contract specification.

- [ ] **Step 1: Add final absence and active-identity tests**

Assert active project files contain the new repository and package identities and do not contain the old GitHub URL, old project script, or old package root. Exclude copied architecture and historical Superpowers documents from this check. Assert the filesystem has no `xplane_fdr` directory and `importlib.util.find_spec("xplane_fdr") is None`.

- [ ] **Step 2: Update handoff and backlog status**

Record that the identity/FDR-kernel increment is implemented but unreleased, list the parent architecture and completed plan, and identify the next required specification as canonical measurement/binding/observation/sample/frame/timing/quality contracts. Keep ARINC and FDM/FOQA in later governed increments. The changelog heading remains `0.1.0 (Unreleased)`.

- [ ] **Step 3: Run the complete source-quality matrix**

Run from a clean post-commit candidate:

```powershell
uv sync --frozen
uv run python -m unittest discover -v
uv run ruff check .
uv run ruff format --check .
uv run ty check
uv run python tools/quality.py check
uv run mkdocs build --strict
git diff --check
```

Expected: every command exits zero. The aggregate quality command must pass Xenon rather than merely print a rank diagnostic.

- [ ] **Step 4: Commit the migration handoff**

```powershell
git add HANDOFF.md CHANGELOG.md BACKLOG.md tests/test_project_metadata.py tests/test_documentation.py
git commit -m "docs: complete xplane-fdau identity migration"
git status --short
```

Expected: commit succeeds and status is empty.

- [ ] **Step 5: Build and validate a fresh immutable artifact pair**

Use a new empty directory rather than reusing artifacts from earlier tasks:

```powershell
$artifactDir = Join-Path $env:TEMP 'xplane-fdau-final-dist'
if (Test-Path -LiteralPath $artifactDir) {
    $resolved = (Resolve-Path -LiteralPath $artifactDir).Path
    $expected = [System.IO.Path]::GetFullPath((Join-Path $env:TEMP 'xplane-fdau-final-dist'))
    if ($resolved -ne $expected) { throw "unexpected artifact directory: $resolved" }
    Remove-Item -LiteralPath $resolved -Recurse -Force
}
New-Item -ItemType Directory -Path $artifactDir | Out-Null
uv build --no-sources --out-dir $artifactDir
uv tool run twine check --strict "$artifactDir\xplane_fdau-0.1.0-py3-none-any.whl" "$artifactDir\xplane_fdau-0.1.0.tar.gz"
uv run python tools/release.py check-dist $artifactDir
Get-FileHash "$artifactDir\xplane_fdau-0.1.0-py3-none-any.whl", "$artifactDir\xplane_fdau-0.1.0.tar.gz" -Algorithm SHA256
```

Expected: exact artifacts pass and hashes are reported. No publication command is run.

- [ ] **Step 6: Run installed-wheel smoke outside the checkout on all supported versions**

Run this exact matrix:

```powershell
$artifactDir = [System.IO.Path]::GetFullPath((Join-Path $env:TEMP 'xplane-fdau-final-dist'))
$wheel = Join-Path $artifactDir 'xplane_fdau-0.1.0-py3-none-any.whl'
$smokeScript = (Resolve-Path -LiteralPath 'tools\installed_smoke.py').Path
foreach ($version in @('3.12', '3.13', '3.14')) {
    $suffix = $version.Replace('.', '')
    $venvPath = [System.IO.Path]::GetFullPath("C:\tmp\xplane-fdau-smoke-$suffix")
    if (Test-Path -LiteralPath $venvPath) {
        $resolved = (Resolve-Path -LiteralPath $venvPath).Path
        if ($resolved -ne $venvPath -or -not $resolved.StartsWith('C:\tmp\xplane-fdau-smoke-')) {
            throw "unexpected smoke directory: $resolved"
        }
        Remove-Item -LiteralPath $resolved -Recurse -Force
    }
    uv venv $venvPath --python $version
    $python = Join-Path $venvPath 'Scripts\python.exe'
    uv pip install --python $python $wheel
    Push-Location 'C:\tmp'
    try {
        & $python $smokeScript 0.1.0
        if ($LASTEXITCODE -ne 0) { throw "installed smoke failed for Python $version" }
    }
    finally {
        Pop-Location
    }
}
```

The smoke must import `xplane_fdau`, reject `xplane_fdr`, load the nested
schema, parse v3/v4, round-trip v4, and execute the nested CLI.

- [ ] **Step 7: Request final code review and resolve only load-bearing findings**

Invoke `superpowers:requesting-code-review` over the merge-base-to-HEAD diff. Review against the parent architecture and this migration specification. Any accepted fix uses `superpowers:receiving-code-review`, `superpowers:systematic-debugging` where applicable, and test-first implementation. Re-run Steps 3–6 after the last fix commit.

## Post-plan integration and local-directory transition

After Task 7 is clean and `superpowers:verification-before-completion` confirms fresh evidence, invoke `superpowers:finishing-a-development-branch`. The user has authorized the rename-in-place migration, but integration must still stop if `main` or either worktree contains unrelated changes.

Use this guarded sequence from the primary checkout:

```powershell
git worktree list --porcelain
git status --short
git merge --ff-only feature/xplane-fdr-core
git worktree remove 'C:\Users\Jeff\source\repos\xp\xplane-fdr\.worktrees\xplane-fdr-core'
git branch -d feature/xplane-fdr-core
git remote get-url origin
```

Verify the resolved worktree path is exactly the linked path shown before removal. Do not manually delete it. Confirm `origin` is the new URL and `main` contains the migration head.

Before renaming the primary checkout directory, verify:

```powershell
$source = (Resolve-Path -LiteralPath 'C:\Users\Jeff\source\repos\xp\xplane-fdr').Path
$target = [System.IO.Path]::GetFullPath('C:\Users\Jeff\source\repos\xp\xplane-fdau')
if ($source -ne 'C:\Users\Jeff\source\repos\xp\xplane-fdr') { throw "unexpected source: $source" }
if (Test-Path -LiteralPath $target) { throw "target already exists: $target" }
git -C $source worktree list --porcelain
git -C $source status --short
```

Only when the source is clean, no linked worktree remains, and the target is
absent, move the directory as one explicit operation:

```powershell
Move-Item -LiteralPath $source -Destination $target
```

Restart the agent/session in
`C:\Users\Jeff\source\repos\xp\xplane-fdau`, then run:

```powershell
uv sync --frozen
uv run python -m unittest discover -v
uv run ruff check .
uv run ruff format --check .
uv run ty check
uv run python tools/quality.py check
uv run mkdocs build --strict
git diff --check
git status --short
git remote get-url origin
```

Every command must exit zero, status must be empty, and the remote must be
`https://github.com/tvproductions/xplane-fdau.git`. Do not push, tag, or
publish.
