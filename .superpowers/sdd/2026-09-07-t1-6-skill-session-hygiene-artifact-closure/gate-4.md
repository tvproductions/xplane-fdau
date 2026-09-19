# T1.6 gate 4

- **Child:** `T1.6`
- **Gate:** `4`
- **Kind:** verification
- **Result:** passed
- **Date:** 2026-09-07
- **Subject:** Governance artifact exclusion

Fresh final artifacts were built at reviewed commit
`3a274fdd5c83954c9b5ecc8ddab6b5e588baec8d`, after independently accepted
correction `ee2805f7357f901f63a0ae44e39ef83625091d8b`. Per controller ruling,
this entire build and installed matrix preceded gate authoring/linking.

## Literal malicious-member regression proof

```powershell
uv run python -m unittest tests.test_project_skills.ProjectSkillTests.test_repository_governance_is_excluded_from_source_builds tests.test_release_tool.ReleaseToolTests.test_check_dist_rejects_every_repository_governance_family -v
uv run python -m unittest tests.test_project_skills tests.test_release_tool tests.test_installed_smoke -v
```

Task 4 at `8033e997ac9dbca19a0178bd50db36877268cb14`: two characterization
tests passed against the existing validator; the expanded 30-test focused run
passed in 1.686s. The build-policy test reads pyproject using standard-library
tomllib and checks `.codex/**`, `.git/**`, `.superpowers/**`, and
`docs/superpowers/**` source exclusions. The exact archive validator remains
unchanged. The malicious-member test creates six independent wheel candidates
and seven independent sdist candidates, adding each of local skill, portable
skill, SDD evidence, BACKLOG, ROADMAP, HANDOFF, and (sdist) Superpowers plan.
All 13 candidates are rejected. The in-memory mutation disabling the overlapping
rejection guards produced 13 assertRaises failures, proving test sensitivity
without modifying production behavior or widening archive contents.

## New immutable pair

```powershell
$t16FinalArtifacts = Join-Path ([System.IO.Path]::GetTempPath()) ('xplane-fdau-t1-6-final-' + [guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $t16FinalArtifacts | Out-Null
uv build --no-sources --out-dir $t16FinalArtifacts
```

Resolved fresh directory:
`C:\Users\Jeff\AppData\Local\Temp\xplane-fdau-t1-6-final-16743d28c5d14a7e9e636feee1aa72b5`.
Build exited 0. This is not Task 4's candidate directory; the pair was built
anew. Identical old/new hashes reflect unchanged product payload.

```powershell
uv tool run twine check --strict 'C:\Users\Jeff\AppData\Local\Temp\xplane-fdau-t1-6-final-16743d28c5d14a7e9e636feee1aa72b5\xplane_fdau-0.1.0-py3-none-any.whl' 'C:\Users\Jeff\AppData\Local\Temp\xplane-fdau-t1-6-final-16743d28c5d14a7e9e636feee1aa72b5\xplane_fdau-0.1.0.tar.gz'
uv run python tools/release.py check-dist 'C:\Users\Jeff\AppData\Local\Temp\xplane-fdau-t1-6-final-16743d28c5d14a7e9e636feee1aa72b5'
```

Both commands exited 0; strict Twine printed PASSED for both files and
check-dist returned the exact filenames and SHA-256 values:

| File | SHA-256 |
| --- | --- |
| xplane_fdau-0.1.0-py3-none-any.whl | 25ac6660fa3b4b1bfd5e431d0a3d7126a126012ad998509639d3f18465802afb |
| xplane_fdau-0.1.0.tar.gz | 5429361eb3d1569cba926bcc0f95c72dda41caa2069bb30f2ed924f6ec52bce6 |

## Installed wheel matrix outside checkout

New matrix root:
`C:\Users\Jeff\AppData\Local\Temp\xplane-fdau-t1-6-matrix-0ae0dcded36c4ff89c7631401b9e2110`.
The following commands describe the exact executed invocations with variables
expanded to the observed immutable paths; each native exit code was checked:

```powershell
$t16MatrixRoot = 'C:\Users\Jeff\AppData\Local\Temp\xplane-fdau-t1-6-matrix-0ae0dcded36c4ff89c7631401b9e2110'
$t16Wheel = 'C:\Users\Jeff\AppData\Local\Temp\xplane-fdau-t1-6-final-16743d28c5d14a7e9e636feee1aa72b5\xplane_fdau-0.1.0-py3-none-any.whl'
$t16Smoke = 'C:\Users\Jeff\source\repos\xp\xplane-fdau\.worktrees\t1-6-skill-closure\tools\installed_smoke.py'
uv venv "$t16MatrixRoot\py312" --python 3.12
& "$t16MatrixRoot\py312\Scripts\python.exe" --version
uv pip install --python "$t16MatrixRoot\py312\Scripts\python.exe" --no-deps $t16Wheel
Push-Location $t16MatrixRoot
& "$t16MatrixRoot\py312\Scripts\python.exe" $t16Smoke 0.1.0
Pop-Location
uv venv "$t16MatrixRoot\py313" --python 3.13
& "$t16MatrixRoot\py313\Scripts\python.exe" --version
uv pip install --python "$t16MatrixRoot\py313\Scripts\python.exe" --no-deps $t16Wheel
Push-Location $t16MatrixRoot
& "$t16MatrixRoot\py313\Scripts\python.exe" $t16Smoke 0.1.0
Pop-Location
uv venv "$t16MatrixRoot\py314" --python 3.14
& "$t16MatrixRoot\py314\Scripts\python.exe" --version
uv pip install --python "$t16MatrixRoot\py314\Scripts\python.exe" --no-deps $t16Wheel
Push-Location $t16MatrixRoot
& "$t16MatrixRoot\py314\Scripts\python.exe" $t16Smoke 0.1.0
Pop-Location
```

| Environment | Observed interpreter | Exact-wheel install | Outside-checkout smoke |
| --- | --- | --- | --- |
| py312 | Python 3.12.13 | exit 0, xplane-fdau==0.1.0 | exit 0, no output |
| py313 | Python 3.13.14 | exit 0, xplane-fdau==0.1.0 | exit 0, no output |
| py314 | Python 3.14.4 | exit 0, xplane-fdau==0.1.0 | exit 0, no output |

Smoke verifies installed origins/version, absence of obsolete identity,
module imports, root exports, nested schema, adjacent CLI, native v3/v4
validation, canonical roundtrip and GeoJSON. No runtime dependencies were
installed. Windows was observed for all three versions; Linux/macOS were not.
The pre-existing uv 0.12.10/configured uv-build <0.12 warning was nonfatal.
Artifacts and environments are retained, not published. No runtime, validator,
dependency, release, remote, or external-repository behavior changed.
