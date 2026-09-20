# xplane-fdau Source-Layout Migration Implementation Plan

- **Governance:** active
- **Status:** in_progress
- **Date:** 2026-08-09
- **Roadmap child:** `B1.1`
- **Source specification:** `docs/superpowers/specs/2026-08-09-src-layout-migration-design.md`
- **Approval:** 2026-09-20 — Jeff / tvproductions
- **Completion evidence:** —

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Move the entire runtime package to `src/xplane_fdau` and prove that source imports, wheel imports, and source archives retain their intended identities.

**Architecture:** The physical checkout root becomes `src/xplane_fdau`. Import names and wheel members remain under `xplane_fdau`, while sdist package members acquire a `src/` prefix. Only package layout, build configuration, physical-path tooling, active guidance, and related tests change.

**Tech Stack:** Python 3.12–3.14, `uv`/`uv_build`, standard-library-only runtime, `unittest`, Ruff, ty, the repository quality and hygiene adapters, MkDocs, and exact artifact validation.

**Spec:** `docs/superpowers/specs/2026-08-09-src-layout-migration-design.md`

## Global Constraints

- `B1.1` has one approved design and verified prerequisite `T2.2`. `T3.1` is independent.
- Preserve distribution `xplane-fdau`, import root `xplane_fdau`, command `xplane-fdau`, version `0.1.0`, public exports, schemas, native FDR behavior, and empty runtime dependency list.
- Preserve every runtime package-file byte during the move. Do not add a root forwarding package or `src.xplane_fdau` import.
- Keep the source package pure Python and standard-library-only. External XPLM, XPPython3, xpwebapi, q4xpcc, and network clients remain outside the distribution.
- Use `unittest` only. Run focused `unittest`, Ruff, and ty checks during edits.
- Package-layout and artifact-validator changes require one full offline hygiene pass at stable closeout. It already runs the active-Python quality gate, strict docs, and a fresh wheel/sdist check; do not repeat that full gate on the unchanged candidate.
- Run installed-wheel smoke outside the checkout on the active supported Python. CI supplies the routine 3.12–3.14 matrix; run a local matrix only if a version-specific issue appears.
- No Git synchronization, tag, publication, or release is implied by this plan.

## File map

| Responsibility | Exact files |
| --- | --- |
| Package layout and build root | `xplane_fdau/**` → `src/xplane_fdau/**`; `pyproject.toml` |
| Source-path and import tests | `tests/test_project_metadata.py`, `tests/test_public_api.py`, `tests/test_runtime_import_boundary.py`, `tests/test_documentation.py` |
| Quality and active path guidance | `tools/quality.py`, `tests/test_quality_tool.py`, `.codex/skills/code-quality/SKILL.md`, `docs/usage/native-fdr.md` |
| Artifact validation and fixtures | `tools/release.py`, `tests/test_release_tool.py`, `tests/test_installed_smoke.py` |
| Delivery evidence and lifecycle | `.superpowers/sdd/2026-08-09-src-layout-migration/`, `BACKLOG.md`, `HANDOFF.md`, this plan |

The allowed import root in `tools/runtime_imports.py` and `[tool.coverage.run].source = ["xplane_fdau"]` remain package names. CI and pre-commit invoke package-independent commands and need no path rewrite.

## Execution entry

After approval, mark this plan `approved` with Jeff's approval date. Use the backlog-status adapter to select `B1.1` (currently no active child), then transition `specified` → `planned` → `in_progress`. For each command below, run it without `--apply`, inspect the proposed diff and audit, then repeat it with its printed `--target-sha256 <digest> --apply`. Commit the approved plan and lifecycle state before implementation.

```powershell
uv run --offline --frozen python .codex/skills/backlog-status/scripts/backlog_status.py select B1.1 --expect-current none
uv run --offline --frozen python .codex/skills/backlog-status/scripts/backlog_status.py transition B1.1 planned --expect specified
uv run --offline --frozen python .codex/skills/backlog-status/scripts/backlog_status.py transition B1.1 in_progress --expect planned
```

Use an isolated worktree for execution under `superpowers:using-git-worktrees` unless the user has already chosen the current checkout. Check its clean baseline before Task 1.

Record the pre-migration baseline before Task 1:

```powershell
$baseline = git rev-parse HEAD
```

Retain this exact commit ID in the B1.1 evidence so it can be used after later task commits.

---

### Task 1: Move the package and prove source import isolation

**Files:**
- Move: `xplane_fdau/**` → `src/xplane_fdau/**`
- Modify: `pyproject.toml`
- Modify: `tests/test_project_metadata.py`
- Modify: `tests/test_public_api.py`
- Modify: `tests/test_runtime_import_boundary.py`
- Modify: `tests/test_documentation.py`

**Interfaces:**
- Consumes: the current `xplane_fdau` import and complete tracked package tree.
- Produces: `src/xplane_fdau` as the only physical package root, `module-root = "src"`, unchanged `xplane_fdau` imports.

- [ ] **Step 1: Write the failing root and interpreter test.** Add `subprocess` and `sys` imports to `tests/test_project_metadata.py` and add this method to `ProjectMetadataTests`:

```python
def test_runtime_package_uses_only_installed_src_layout(self) -> None:
    root = Path(__file__).resolve().parents[1]
    project = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))
    self.assertEqual("src", project["tool"]["uv"]["build-backend"]["module-root"])
    self.assertTrue((root / "src/xplane_fdau/__init__.py").is_file())
    self.assertFalse((root / "xplane_fdau").exists())
    result = subprocess.run(
        [sys.executable, "-c", "from pathlib import Path; import xplane_fdau; print(Path(xplane_fdau.__file__).resolve())"],
        cwd=root, capture_output=True, text=True, check=True,
    )
    self.assertTrue(Path(result.stdout.strip()).is_relative_to((root / "src/xplane_fdau").resolve()))
```

- [ ] **Step 2: Make source enumeration tests fail for an empty scan.** In `tests/test_runtime_import_boundary.py`, use `ROOT / "src/xplane_fdau"` and assert that the collected `*.py` path tuple is nonempty before checking violations. In `tests/test_public_api.py`, use `project_root / "src" / "xplane_fdau"` for `formats_root` and `sink_path`; in `_resolve_import`, compute module parts relative to `project_root / "src"` so the resolved name still begins with `xplane_fdau`. In `tests/test_documentation.py`, retarget the packaged schema and runtime `*.py` scan to `ROOT / "src/xplane_fdau"` and assert the scan is nonempty.

Use these exact expressions in the relevant tests:

```python
runtime_paths = tuple(sorted((ROOT / "src/xplane_fdau").rglob("*.py")))
self.assertTrue(runtime_paths)
formats_root = project_root / "src" / "xplane_fdau" / "formats"
sink_path = project_root / "src" / "xplane_fdau" / "sinks" / "xplane_fdr.py"
module_parts = list(path.relative_to(project_root / "src").with_suffix("").parts)
packaged = ROOT / "src/xplane_fdau/formats/xplane_fdr/schemas/fdr-record-config-v1.schema.json"
```

- [ ] **Step 3: Verify RED.** Run `uv run --offline --frozen python -m unittest tests.test_project_metadata tests.test_public_api tests.test_runtime_import_boundary tests.test_documentation -v`. Expect failures from the missing `src` tree, flat `module-root`, and empty source scans; unrelated assertions should still pass.

- [ ] **Step 4: Make the one tracked move and change the build root.**

```powershell
if (Test-Path -LiteralPath src/xplane_fdau) { throw "src package already exists" }
New-Item -ItemType Directory -Path src | Out-Null
git mv xplane_fdau src/xplane_fdau
```

Set `[tool.uv.build-backend].module-root` in `pyproject.toml` to `"src"`. Keep every existing `source-exclude` entry, `[project]` field, and `[tool.coverage.run].source` unchanged. Check `git diff --cached --find-renames --summary`: every package file should be a byte-identical rename.

- [ ] **Step 5: Sync and verify GREEN.** Run `uv sync --offline --frozen`, then repeat the focused `unittest` command from Step 3. Run `uv run --offline --frozen ruff check src/xplane_fdau tests/test_project_metadata.py tests/test_public_api.py tests/test_runtime_import_boundary.py tests/test_documentation.py`, `uv run --offline --frozen ruff format --check src/xplane_fdau tests/test_project_metadata.py tests/test_public_api.py tests/test_runtime_import_boundary.py tests/test_documentation.py`, and `uv run --offline --frozen ty check`. All must pass.

- [ ] **Step 6: Commit.** Stage the moved tree, `pyproject.toml`, and four named test files. Run `git diff --cached --check` and commit as `build: isolate runtime package under src`.

### Task 2: Retarget quality checks and active source guidance

**Files:**
- Modify: `tools/quality.py`
- Modify: `tests/test_quality_tool.py`
- Modify: `.codex/skills/code-quality/SKILL.md`
- Modify: `docs/usage/native-fdr.md`
- Modify: `tests/test_documentation.py`

**Interfaces:**
- Consumes: `src/xplane_fdau` from Task 1.
- Produces: `tools.quality.SOURCE_PATH = "src/xplane_fdau"` and source-aware checks that scan that directory; coverage and imports continue to name `xplane_fdau`.

- [ ] **Step 1: Write failing quality-path assertions.** In `test_quality_targets_only_the_renamed_runtime_root`, assert `quality.SOURCE_PATH == "src/xplane_fdau"`, `quality.SOURCE_PATHS == ("src/xplane_fdau", "tests", "tools")`, and that each source-oriented command (`ruff`, `bandit`, `interrogate`, `vulture`, `lizard`, `cohesion`, `wily`, `xenon`) contains `src/xplane_fdau` as a complete argument wherever it currently contains the flat physical path. Assert `"xplane_fdau"` is not a complete path argument in those commands. Keep the existing gate-order, coverage-count, and forbidden-import assertions.

Use an argument-level assertion so import-name strings cannot satisfy it:

```python
self.assertEqual("src/xplane_fdau", quality.SOURCE_PATH)
self.assertEqual(("src/xplane_fdau", "tests", "tools"), quality.SOURCE_PATHS)
source_steps = {
    "ruff check", "ruff format --check", "ruff format", "bandit",
    "interrogate", "vulture", "lizard report", "cohesion report",
    "wily build", "wily report", "xenon complexity",
}
for steps in quality.COMMANDS.values():
    for step in steps:
        if step.name in source_steps:
            self.assertIn(quality.SOURCE_PATH, step.command)
            self.assertNotIn("xplane_fdau", step.command)
```

- [ ] **Step 2: Write a failing active-link assertion.** In `tests/test_documentation.py`, assert `docs/usage/native-fdr.md` contains `blob/main/src/xplane_fdau/formats/xplane_fdr/schemas/fdr-record-config-v1.schema.json`. The current link lacks `src/`.

Add this assertion to the existing documented-schema test:

```python
guide = (ROOT / "docs/usage/native-fdr.md").read_text(encoding="utf-8")
self.assertIn(
    "blob/main/src/xplane_fdau/formats/xplane_fdr/schemas/fdr-record-config-v1.schema.json",
    guide,
)
```

- [ ] **Step 3: Verify RED.** Run `uv run --offline --frozen python -m unittest tests.test_quality_tool tests.test_documentation -v`. Expect only the new physical-path and link assertions to fail.

- [ ] **Step 4: Change the physical command arguments.** Define `SOURCE_PATH = "src/xplane_fdau"` and `SOURCE_PATHS = (SOURCE_PATH, "tests", "tools")` in `tools/quality.py`. Replace the flat physical argument in Bandit, Interrogate, Lizard, Cohesion, Wily, and Xenon steps with `SOURCE_PATH`. Ruff and Vulture already consume `SOURCE_PATHS`. Keep coverage's import-package setting unchanged.

- [ ] **Step 5: Change the two active guidance paths.** In `.codex/skills/code-quality/SKILL.md`, use `src/xplane_fdau` in both explicit focused Ruff commands. In `docs/usage/native-fdr.md`, change only the GitHub source-schema link to `https://github.com/tvproductions/xplane-fdau/blob/main/src/xplane_fdau/formats/xplane_fdr/schemas/fdr-record-config-v1.schema.json`; keep public Python imports unchanged.

- [ ] **Step 6: Verify GREEN and commit.** Repeat Step 3, then run `uv run --offline --frozen ruff check tools/quality.py tests/test_quality_tool.py tests/test_documentation.py`, `uv run --offline --frozen ruff format --check tools/quality.py tests/test_quality_tool.py tests/test_documentation.py`, and `uv run --offline --frozen ty check`. Run `git diff --check`, stage the five named files, and commit as `build: retarget source quality checks`.

### Task 3: Preserve exact wheel and sdist validation

**Files:**
- Modify: `tools/release.py`
- Modify: `tests/test_release_tool.py`
- Modify: `tests/test_installed_smoke.py`

**Interfaces:**
- Consumes: `src/xplane_fdau` and `module-root = "src"`.
- Produces: `_expected_package_files() -> dict[str, bytes]` keyed by wheel-relative `xplane_fdau/...` names; `_check_package_payloads(read: Callable[[str], bytes], names: set[str], version: str, *, label: str, prefix: str = "") -> None` validates wheel or `src/`-prefixed sdist payloads.

- [ ] **Step 1: Make synthetic artifacts express the new split.** In `ReleaseToolTests._package_files`, enumerate `Path("src/xplane_fdau")` and key each file with `source.relative_to(Path("src")).as_posix()`. In `_make_dist`, keep wheel package directories unchanged; prefix every tar package file with `xplane_fdau-0.1.0/src/` and add `xplane_fdau-0.1.0/src` plus its nested package directories. Retarget the package-payload corruption and hostile tar link cases to `xplane_fdau-0.1.0/src/xplane_fdau/...`, leaving project-root metadata attacks as they are.

Keep the fixture's wheel-relative keys and add the prefix only when creating tar members:

```python
source_root = Path("src/xplane_fdau")
files[source.relative_to(source_root.parent).as_posix()] = source.read_bytes()
tar_files = {
    f"xplane_fdau-0.1.0/src/{name}": payload
    for name, payload in self._package_files().items()
}
```

- [ ] **Step 2: Add explicit positive and negative layout tests.** The existing complete-artifact test must accept the new fixture without changing wheel filenames. Add a test that inserts `xplane_fdau-0.1.0/xplane_fdau/__init__.py` into the tar and expects `ReleaseError` for an extra flat member. Add a test that inserts `src/xplane_fdau/hostile.py` into the wheel and expects `ReleaseError`. Retain all existing duplicate, link, unsafe-path, metadata, RECORD, and payload-byte cases.

Use the existing `_make_dist` helper for both negative controls:

```python
def test_rejects_flat_package_member_in_src_sdist(self) -> None:
    with tempfile.TemporaryDirectory() as raw:
        directory = Path(raw)
        self._make_dist(
            directory,
            tar_updates={"xplane_fdau-0.1.0/xplane_fdau/__init__.py": b""},
        )
        with self.assertRaisesRegex(release.ReleaseError, "sdist members differ"):
            release.check_dist(directory)

def test_rejects_src_prefix_in_wheel(self) -> None:
    with tempfile.TemporaryDirectory() as raw:
        directory = Path(raw)
        self._make_dist(directory, wheel_updates={"src/xplane_fdau/hostile.py": b""})
        with self.assertRaisesRegex(release.ReleaseError, "outside the package"):
            release.check_dist(directory)
```

- [ ] **Step 3: Verify RED.** Run `uv run --offline --frozen python -m unittest tests.test_release_tool tests.test_installed_smoke -v`. Expect release validation to fail because `tools/release.py` still reads the flat checkout root and expects flat sdist members.

- [ ] **Step 4: Separate checkout and archive names in `tools/release.py`.** Add `SOURCE_ROOT = ROOT / "src" / PACKAGE` and change `_version` to read `SOURCE_ROOT / "__init__.py"`. Replace `_expected_package_files` with:

```python
def _expected_package_files() -> dict[str, bytes]:
    expected: dict[str, bytes] = {}
    for source in SOURCE_ROOT.rglob("*"):
        if source.is_file() and (source.suffix in {".py", ".json"} or source.name == "py.typed"):
            expected[source.relative_to(SOURCE_ROOT.parent).as_posix()] = source.read_bytes()
    return expected
```

Add a `prefix: str = ""` keyword to `_check_package_payloads`. Compare package members to `{f"{prefix}{name}" for name in expected}`; read payload and `__init__.py` through `read(f"{prefix}{name}")`. Call it with the default prefix for the wheel and `prefix="src/"` for the sdist. In `_check_sdist`, build `expected_relative` from `{f"src/{name}" for name in _expected_package_files()}` plus `PKG-INFO`, `pyproject.toml`, `pyproject.toml.orig`, `LICENSE`, and `README.md`. Keep exact directory, metadata, license, content, unsafe-member, and wheel checks intact.

- [ ] **Step 5: Retarget the installed-smoke unit fixture.** In `tests/test_installed_smoke.py`, make the checkout-path rejection case pass `checkout / "src/xplane_fdau/__init__.py"`. Leave import names and command names unchanged.

- [ ] **Step 6: Verify GREEN and commit.** Repeat Step 3, then run `uv run --offline --frozen ruff check tools/release.py tests/test_release_tool.py tests/test_installed_smoke.py`, `uv run --offline --frozen ruff format --check tools/release.py tests/test_release_tool.py tests/test_installed_smoke.py`, and `uv run --offline --frozen ty check`. Run `git diff --check`, stage the three named files, and commit as `build: validate src layout distributions`.

### Task 4: Verify the installed artifact and close B1.1

**Files:**
- Create: `.superpowers/sdd/2026-08-09-src-layout-migration/gate-1.md` through `gate-5.md`, `review.md`, and `completion.md`
- Modify: `BACKLOG.md` through the backlog-status adapter
- Modify: `HANDOFF.md`
- Modify: this plan's status and completion metadata

**Interfaces:**
- Consumes: Tasks 1–3 and their passing focused tests.
- Produces: fresh artifact, installed-smoke, and independent-review evidence; `B1.1` reaches `verified` only after all five gates pass.

- [ ] **Step 1: Inspect the final candidate and prove the package move preserved bytes.** The pre-migration `$baseline` is the commit recorded in the execution entry. If using a new shell, set `$baseline` to that exact recorded SHA. Require a clean candidate, then compare the tracked relative package paths, Git modes, and blob hashes at `$baseline` and `HEAD`:

```powershell
$ErrorActionPreference = "Stop"
$status = @(git status --porcelain --untracked-files=all)
if ($LASTEXITCODE -ne 0 -or $status.Count -ne 0) { throw "candidate worktree is not clean" }
git diff --check
if ($LASTEXITCODE -ne 0) { throw "diff check failed" }
if (Test-Path -LiteralPath xplane_fdau) { throw "flat package still exists" }
if (-not (Test-Path -LiteralPath src/xplane_fdau/__init__.py)) { throw "src package is missing" }

function Get-PackageBlobMap([string]$revision, [string]$prefix) {
    $entries = @(git ls-tree -r $revision -- $prefix)
    if ($LASTEXITCODE -ne 0) { throw "git ls-tree failed for $revision" }
    return @($entries | ForEach-Object {
        $fields = $_ -split "`t", 2
        $metadata = $fields[0] -split " "
        $relative = $fields[1].Substring($prefix.Length + 1)
        "$relative`t$($metadata[0])`t$($metadata[2])"
    } | Sort-Object)
}
$before = @(Get-PackageBlobMap $baseline "xplane_fdau")
$after = @(Get-PackageBlobMap "HEAD" "src/xplane_fdau")
if ($before.Count -eq 0 -or $before.Count -ne $after.Count -or
    @(Compare-Object -ReferenceObject $before -DifferenceObject $after).Count -ne 0) {
    throw "tracked package paths, modes, or bytes changed during the move"
}
Write-Output "matched $($before.Count) tracked package files byte-for-byte"
```

Save the comparison output and both commit IDs in `gate-1.md`. If a fix is needed, use a failing focused `unittest` first and rerun focused Ruff and ty.

- [ ] **Step 2: Run the complete offline package-layout gate once.**

```powershell
uv run --offline --frozen python .codex/skills/hygiene/scripts/hygiene.py
```

Record its result, active Python version, `unittest` count, quality result, strict MkDocs result, artifact names, and exact inventory result. This command already runs `tools/quality.py check` once. If any code changes after it, rerun hygiene once on the new stable candidate.

- [ ] **Step 3: Prove installed-wheel isolation on the active Python.** Create a separate temporary artifact directory outside the checkout, build one wheel/sdist pair, validate it before creating a venv in that directory, install the wheel offline, and run the installed smoke from that directory:

```powershell
$ErrorActionPreference = "Stop"
$artifactRoot = Join-Path ([System.IO.Path]::GetTempPath()) ("xplane-fdau-b1-1-" + [guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Path $artifactRoot | Out-Null
uv build --offline --no-sources --out-dir $artifactRoot
if ($LASTEXITCODE -ne 0) { throw "wheel/sdist build failed; preserve $artifactRoot" }
uv run --offline --frozen python tools/release.py check-dist $artifactRoot
if ($LASTEXITCODE -ne 0) { throw "artifact validation failed; preserve $artifactRoot" }
$smokeEnv = Join-Path $artifactRoot "smoke"
uv run --offline --frozen python -m venv $smokeEnv
if ($LASTEXITCODE -ne 0) { throw "smoke environment creation failed; preserve $artifactRoot" }
$python = Join-Path $smokeEnv "Scripts/python.exe"
$wheel = Join-Path $artifactRoot "xplane_fdau-0.1.0-py3-none-any.whl"
uv pip install --offline --python $python $wheel
if ($LASTEXITCODE -ne 0) { throw "wheel installation failed; preserve $artifactRoot" }
$smokeScript = (Resolve-Path -LiteralPath tools/installed_smoke.py).Path
Push-Location $artifactRoot
try {
    & $python $smokeScript 0.1.0
    if ($LASTEXITCODE -ne 0) { throw "installed smoke failed; preserve $artifactRoot" }
    & $python -c "import xplane_fdau; print(xplane_fdau.__file__)"
    if ($LASTEXITCODE -ne 0) { throw "installed import location check failed; preserve $artifactRoot" }
}
finally { Pop-Location }
```

Record the wheel and sdist SHA-256 values from `check-dist` and the installed `xplane_fdau.__file__` location. Preserve the temporary directory on failure. On success, remove only the verified temporary directory:

```powershell
$resolvedArtifactRoot = (Resolve-Path -LiteralPath $artifactRoot).Path
$tempParent = [System.IO.Path]::GetFullPath([System.IO.Path]::GetTempPath()).TrimEnd('\', '/')
if ([System.IO.Path]::GetDirectoryName($resolvedArtifactRoot) -ne $tempParent -or
    -not [System.IO.Path]::GetFileName($resolvedArtifactRoot).StartsWith("xplane-fdau-b1-1-")) {
    throw "unexpected artifact directory: $resolvedArtifactRoot"
}
Remove-Item -LiteralPath $resolvedArtifactRoot -Recurse -Force
```

- [ ] **Step 4: Obtain independent review.** Use `superpowers:requesting-code-review` against the implementation diff. Review the five B1.1 gates, source-byte preservation, active physical-path references, import isolation, wheel/sdist parity, hostile-archive tests, and no release action. Save the accepted review to `review.md`. Address every load-bearing finding before proceeding, then rerun affected focused checks and Steps 2–3 on the final candidate.

- [ ] **Step 5: Record five gate receipts and lifecycle transitions.** Write one receipt per B1.1 acceptance gate with exact command output and commit/artifact identities, then write `completion.md`. Mark this plan `completed` with the completion-evidence link and update `HANDOFF.md` to point to `C1.1` as the next canonical child. Use backlog-status dry-run/hash/apply for each gate and transition; do not hand-edit managed cells. Transition `in_progress` → `implemented` → `reviewed` (with `--review .superpowers/sdd/2026-08-09-src-layout-migration/review.md`) → `verified` only after all gate receipts and review pass. Clear the active-child selection after verification.

```powershell
uv run --offline --frozen python .codex/skills/backlog-status/scripts/backlog_status.py record-gate B1.1 1 --expect-open --evidence .superpowers/sdd/2026-08-09-src-layout-migration/gate-1.md
uv run --offline --frozen python .codex/skills/backlog-status/scripts/backlog_status.py transition B1.1 implemented --expect in_progress
uv run --offline --frozen python .codex/skills/backlog-status/scripts/backlog_status.py transition B1.1 reviewed --expect implemented --review .superpowers/sdd/2026-08-09-src-layout-migration/review.md
uv run --offline --frozen python .codex/skills/backlog-status/scripts/backlog_status.py transition B1.1 verified --expect reviewed
uv run --offline --frozen python .codex/skills/backlog-status/scripts/backlog_status.py select none --expect-current B1.1
```

Repeat the record-gate command with ordinals 2, 3, 4, and 5 and their matching receipt files. Apply each candidate with the tool's printed target hash before preparing the next mutation. Run the strict backlog audit, focused documentation checks, and `git diff --check` after governance edits. Commit evidence and governance, then run `git status --short --branch`. No tag, publication, or release follows.

## Plan self-review

- B1.1 gate 1: Task 1 package move and `module-root` test.
- B1.1 gate 2: Tasks 1–3 source scanners, quality paths, docs link, and release validator.
- B1.1 gate 3: Task 1 repository-root subprocess and Task 4 installed-wheel smoke.
- B1.1 gate 4: Task 3 exact wheel and prefixed sdist inventory and payload tests.
- B1.1 gate 5: Task 4 hygiene, independent review, and evidence receipts.
