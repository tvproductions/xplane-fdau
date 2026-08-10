# xplane-fdau Source-Layout Migration Implementation Plan

- **Governance:** active
- **Status:** draft
- **Date:** 2026-08-09
- **Roadmap child:** `B1.1`
- **Source specification:** `docs/superpowers/specs/2026-08-09-src-layout-migration-design.md`
- **Approval:** —
- **Completion evidence:** —

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Move the xplane-fdau runtime package to `src/xplane_fdau` while preserving imports, wheel contents, native FDR behavior, and strict artifact validation.

**Architecture:** Treat physical checkout paths and installed package paths as separate contracts. Source-aware tooling targets `src/xplane_fdau`; imports and wheel members remain `xplane_fdau`; source-archive members gain the `src/` prefix. Move the package once, then update only path-sensitive configuration, tools, tests, and governance evidence.

**Tech Stack:** Python 3.12–3.14, standard library at runtime, `uv`/`uv_build`, Python `unittest`, Ruff, ty, coverage, Bandit, MkDocs, and repository-owned release tooling.

## Global Constraints

- Governing specification: `docs/superpowers/specs/2026-08-09-src-layout-migration-design.md`.
- Roadmap child: `B1.1`; do not implement canonical-contract or T1 tooling work.
- Runtime remains pure Python and standard-library-only.
- Import name remains `xplane_fdau`; never introduce `src.xplane_fdau` imports.
- Wheel members remain under `xplane_fdau/`; sdist members move under `src/xplane_fdau/`.
- Preserve all package bytes during the move except separately reviewed path-sensitive edits.
- Use Python's `unittest` framework exclusively.
- Do not push, tag, publish, or create a release while executing this plan.

---

### Task 1: Establish the source-layout and quality-path contract

**Files:**
- Modify: `tests/test_project_metadata.py`
- Modify: `tests/test_quality_tool.py`
- Modify: `tests/test_documentation.py`
- Modify: `tests/test_public_api.py`
- Modify: `tests/test_runtime_import_boundary.py`
- Modify: `pyproject.toml`
- Modify: `tools/quality.py`
- Move: `xplane_fdau/` to `src/xplane_fdau/`

**Interfaces:**
- Consumes: existing distribution identity `xplane-fdau` and import identity `xplane_fdau`.
- Produces: physical source root `src/xplane_fdau`, build-backend root `src`, and `tools.quality.SOURCE_PATH = "src/xplane_fdau"`.

- [ ] **Step 1: Add the failing metadata and import-isolation contract**

Add `ROOT = Path(__file__).resolve().parents[1]` and this test to
`ProjectMetadataTests`:

```python
def test_runtime_package_uses_the_src_layout(self) -> None:
    document = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    self.assertEqual("src", document["tool"]["uv"]["build-backend"]["module-root"])
    self.assertTrue((ROOT / "src/xplane_fdau/__init__.py").is_file())
    self.assertFalse((ROOT / "xplane_fdau").exists())

    import xplane_fdau

    module_path = Path(xplane_fdau.__file__).resolve()
    self.assertTrue(module_path.is_relative_to((ROOT / "src/xplane_fdau").resolve()))
```

- [ ] **Step 2: Change the quality-tool expectation before implementation**

Change `test_quality_targets_only_the_renamed_runtime_root` to assert:

```python
self.assertEqual("src/xplane_fdau", quality.SOURCE_PATH)
self.assertEqual(("src/xplane_fdau", "tests", "tools"), quality.SOURCE_PATHS)
self.assertIn("src/xplane_fdau", commands)
self.assertNotIn('"xplane_fdau"', commands)
```

- [ ] **Step 3: Run the focused tests and verify the expected failures**

Run:

```powershell
uv run python -m unittest tests.test_project_metadata tests.test_quality_tool -v
```

Expected: FAIL because `module-root` is empty, `src/xplane_fdau` is absent, the
root package exists, and quality commands still target `xplane_fdau`.

- [ ] **Step 4: Move the tracked package and change the build root**

Run:

```powershell
New-Item -ItemType Directory -Path src
git mv xplane_fdau src/xplane_fdau
```

Change `pyproject.toml` to:

```toml
[tool.uv.build-backend]
module-root = "src"
source-exclude = [
```

Keep the existing `source-exclude` entries unchanged.

- [ ] **Step 5: Centralize the physical source path in the quality tool**

At the top of `tools/quality.py`, define:

```python
SOURCE_PATH = "src/xplane_fdau"
SOURCE_PATHS = (SOURCE_PATH, "tests", "tools")
```

Replace every physical `"xplane_fdau"` argument used by Bandit, interrogate,
lizard, cohesion, wily, and xenon with `SOURCE_PATH`. Keep module-name and
import-name strings unchanged elsewhere.

- [ ] **Step 6: Retarget tests that enumerate physical source files**

Make these exact path changes:

```python
# tests/test_documentation.py
packaged = ROOT / "src/xplane_fdau/formats/xplane_fdr/schemas/fdr-record-config-v1.schema.json"
runtime_paths = tuple(sorted((ROOT / "src/xplane_fdau").rglob("*.py")))

# tests/test_public_api.py
source_root = project_root / "src" / "xplane_fdau"
formats_root = source_root / "formats"
sink_path = source_root / "sinks" / "xplane_fdr.py"
```

In `_resolve_import`, compute module parts relative to `project_root / "src"`
so resolved names still begin with `xplane_fdau`. In
`tests/test_runtime_import_boundary.py`, enumerate
`ROOT / "src/xplane_fdau"` and keep filenames relative to `ROOT`.

- [ ] **Step 7: Synchronize the editable installation and rerun focused tests**

Run:

```powershell
uv sync --frozen
uv run python -m unittest tests.test_project_metadata tests.test_quality_tool tests.test_documentation tests.test_public_api tests.test_runtime_import_boundary -v
```

Expected: PASS; `xplane_fdau.__file__` resolves beneath `src/xplane_fdau`.

- [ ] **Step 8: Commit the source-layout foundation**

Run:

```powershell
git add -- pyproject.toml src/xplane_fdau tools/quality.py tests/test_project_metadata.py tests/test_quality_tool.py tests/test_documentation.py tests/test_public_api.py tests/test_runtime_import_boundary.py
git diff --cached --check
git commit -m "build: move runtime package under src"
```

---

### Task 2: Preserve exact wheel and source-archive validation

**Files:**
- Modify: `tools/release.py`
- Modify: `tests/test_release_tool.py`
- Modify: `tests/test_installed_smoke.py`

**Interfaces:**
- Consumes: physical source root `ROOT / "src" / PACKAGE` from Task 1.
- Produces: wheel-relative package map `xplane_fdau/...` and sdist-relative package map `src/xplane_fdau/...` with identical payload bytes.

- [ ] **Step 1: Change release fixtures to express distinct wheel and sdist paths**

In `ReleaseToolTests`, define:

```python
SOURCE_ROOT = Path("src/xplane_fdau")

def _package_files(self) -> dict[str, bytes]:
    files: dict[str, bytes] = {}
    for source in SOURCE_ROOT.rglob("*"):
        if source.is_file() and (source.suffix in {".py", ".json"} or source.name == "py.typed"):
            wheel_name = source.relative_to(SOURCE_ROOT.parent).as_posix()
            files[wheel_name] = source.read_bytes()
    return files
```

Build tar fixture entries as
`f"xplane_fdau-0.1.0/src/{name}"` for each wheel-relative package name. Add
`xplane_fdau-0.1.0/src` and the corresponding `src/xplane_fdau` directory tree
to the explicit tar directory list. Change the hostile sdist link path to
`xplane_fdau-0.1.0/src/xplane_fdau/link.py`.

- [ ] **Step 2: Add an explicit archive-layout assertion**

Add:

```python
def test_check_dist_accepts_src_layout_without_changing_wheel_layout(self) -> None:
    with tempfile.TemporaryDirectory() as raw:
        directory = Path(raw)
        self._make_dist(directory)
        artifacts = release.check_dist(directory)
        self.assertEqual("xplane_fdau-0.1.0-py3-none-any.whl", artifacts.wheel.name)
        self.assertEqual("xplane_fdau-0.1.0.tar.gz", artifacts.sdist.name)
```

- [ ] **Step 3: Run the release tests and verify the expected failures**

Run:

```powershell
uv run python -m unittest tests.test_release_tool tests.test_installed_smoke -v
```

Expected: FAIL because `tools/release.py` still reads the runtime version and
expected package files from the old root and still expects root-level package
members in the sdist.

- [ ] **Step 4: Separate checkout, wheel, and sdist paths in the release tool**

Add:

```python
SOURCE_ROOT = ROOT / "src" / PACKAGE
SOURCE_PARENT = SOURCE_ROOT.parent
SDIST_SOURCE_PREFIX = "src"
```

Change `_version()` to read `SOURCE_ROOT / "__init__.py"`. Change
`_expected_package_files()` to enumerate `SOURCE_ROOT` and key each payload by
`source.relative_to(SOURCE_PARENT).as_posix()`, preserving wheel names such as
`xplane_fdau/__init__.py`.

In `_check_sdist`, derive:

```python
expected_package = _expected_package_files()
expected_sdist_package = {f"{SDIST_SOURCE_PREFIX}/{name}" for name in expected_package}
expected_relative = expected_sdist_package | {
    "PKG-INFO",
    "pyproject.toml",
    "pyproject.toml.orig",
    "LICENSE",
    "README.md",
}
```

Validate package payloads with a reader that maps wheel-relative names to
`read(f"src/{name}")` and with the wheel-relative package-name set. Do not
change `_check_wheel` member names.

- [ ] **Step 5: Update installed-smoke checkout paths only where physical**

In `tests/test_installed_smoke.py`, change checkout source fixtures from
`checkout / "xplane_fdau/__init__.py"` to
`checkout / "src/xplane_fdau/__init__.py"`. Keep expected import names,
console-script names, and wheel paths unchanged.

- [ ] **Step 6: Run focused artifact tests**

Run:

```powershell
uv run python -m unittest tests.test_release_tool tests.test_installed_smoke -v
```

Expected: PASS, including hostile-member and exact-member tests.

- [ ] **Step 7: Commit artifact-path preservation**

Run:

```powershell
git add -- tools/release.py tests/test_release_tool.py tests/test_installed_smoke.py
git diff --cached --check
git commit -m "build: preserve src layout artifact contracts"
```

---

### Task 3: Verify installed isolation and close B1.1 implementation

**Files:**
- Create: `.superpowers/sdd/2026-08-09-src-layout-migration/verification.md`
- Modify: `BACKLOG.md`
- Modify: `HANDOFF.md`
- Modify: `docs/superpowers/specs/2026-08-09-src-layout-migration-design.md`
- Modify: `docs/superpowers/plans/2026-08-09-src-layout-migration.md`

**Interfaces:**
- Consumes: passing source-layout and artifact contracts from Tasks 1–2.
- Produces: committed verification record, completed plan, and `B1.1` state `implemented` pending independent review.

- [ ] **Step 1: Run the complete repository verification**

Run:

```powershell
uv sync --frozen
uv run python tools/quality.py check
uv run mkdocs build --strict
```

Expected: all blocking checks and all `unittest` cases pass.

- [ ] **Step 2: Build and validate fresh distributions outside the checkout tree**

Run:

```powershell
$artifactRoot = Join-Path ([System.IO.Path]::GetTempPath()) ("xplane-fdau-src-layout-" + [guid]::NewGuid())
New-Item -ItemType Directory -Path $artifactRoot
uv build --no-sources --out-dir $artifactRoot
uv tool run twine check --strict "$artifactRoot\*"
uv run python tools/release.py check-dist $artifactRoot
```

Expected: exactly one universal wheel and one sdist validate; the wheel contains
`xplane_fdau/...`, and the sdist contains `src/xplane_fdau/...`.

- [ ] **Step 3: Run the installed matrix from isolated environments**

Run for Python 3.12, 3.13, and 3.14:

```powershell
$repoRoot = git rev-parse --show-toplevel
$wheel = Get-ChildItem -LiteralPath $artifactRoot -Filter 'xplane_fdau-0.1.0-py3-none-any.whl' | Select-Object -ExpandProperty FullName
foreach ($version in @('3.12', '3.13', '3.14')) {
    $venv = Join-Path $artifactRoot "venv-$version"
    uv venv --python $version $venv
    $python = Join-Path $venv 'Scripts\python.exe'
    uv pip install --python $python $wheel
    Push-Location $artifactRoot
    & $python (Join-Path $repoRoot 'tools\installed_smoke.py') '0.1.0'
    Pop-Location
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}
```

Expected: all three interpreters import the installed wheel outside the checkout
and pass schema, fixture, canonical-write, and console-script smoke checks.

- [ ] **Step 4: Record verification and update governance state**

Create the verification report with the exact commands, test count, artifact
names, SHA-256 values printed by `tools/release.py`, installed Python versions,
and a statement that no tag, package publication, or release occurred.

Update the plan metadata to `completed` with the verification link. Update the
design status to `implemented`. In `BACKLOG.md`, set `B1.1` to `implemented`,
set its gate count to `5/5`, check its five gates with the verification link,
and leave it short of `reviewed`/`verified` until independent review. Update
`HANDOFF.md` to name that review gate.

- [ ] **Step 5: Run final document and scope checks**

Run:

```powershell
git diff --check
uv run python -m unittest tests.test_documentation tests.test_project_metadata tests.test_release_tool tests.test_installed_smoke -v
git status --short
```

Expected: checks pass and only plan-scoped files are modified.

- [ ] **Step 6: Commit the completed migration**

Run:

```powershell
git add -- .superpowers/sdd/2026-08-09-src-layout-migration/verification.md BACKLOG.md HANDOFF.md docs/superpowers/specs/2026-08-09-src-layout-migration-design.md docs/superpowers/plans/2026-08-09-src-layout-migration.md
git diff --cached --check
git commit -m "docs: record src layout migration evidence"
git status -sb
```

Expected: clean worktree with `B1.1` implemented and awaiting independent
review; no push or release action occurs in this plan.
