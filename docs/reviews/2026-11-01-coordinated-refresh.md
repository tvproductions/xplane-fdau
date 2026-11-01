# Coordinated refresh — November 1, 2026

Status: project refresh verified, with the upstream Windows helper status
limitation recorded below. Jeff authorized applying and verifying the
reviewed refresh in chat. This record concerns crosscutting maintenance only;
it does not close STRICT onboarding acceptance or advance a product child.

## Scope and provenance

Rollback: `7438a125e8a2bd5bc2453fe5f73d87b407585c69` on main. Implementation:
`chore/coordinated-refresh-2026-11-01` in its isolated worktree. Preserve the
unrelated October 18 dependency-refresh worktree.

| Surface | Before | Target |
| --- | --- | --- |
| Python | 3.12.16 | Retained; support remains `>=3.12,<3.13` |
| uv / uv_build | 0.13.5 | 0.13.6 |
| Ruff | 0.17.2 | 0.17.3 |
| ty | 0.0.92 | 0.0.95 |
| setup-uv | 10.3.2 | 10.3.3 / `68559e99cc807c1eb7e9238fd43a15bba460eec2` |
| Starter | 0.6.0 / `c0a6945b2170e1cf5bee3e80738916f5b62d13a5` | 0.8.0 / `e0b752fcc13b87ec7868fe0b0f85badefdb6bf52` |
| Superpowers | 7.0.0 / `bb92a77741419a4ab5f06e711a283343f1ada0c3` | 7.0.1 / `2ce8aa15d05bd57213e6f746f953aafb7ded7a8b` |
| gz-skills | 0.8.0 / `75bcd11ee9371ecff1a7b3432d2af29d4bdbb788` | 0.8.3 / `d6acc26e28ca1c4f43e5bb46d8973021d7d006c3` |
| Backplane | `d0eeee829c491da02351e793544aa16ad96461bf` | Retained, disabled; no stable release observed |

Official evidence: [starter release](https://github.com/tvproductions/gz-skills-first-starter/releases/tag/v0.8.0),
[uv release](https://github.com/astral-sh/uv/releases/tag/0.13.6),
[Ruff release](https://github.com/astral-sh/ruff/releases/tag/0.17.3),
[ty release](https://github.com/astral-sh/ty/releases/tag/0.0.95),
[Python release](https://www.python.org/downloads/release/python-31216/).
Official PyPI Index JSON inventory covered 133 locked packages. Initial direct
status failed because global uv had already advanced to 0.13.6 while the project
required 0.13.5; read-only tree, metadata and audit succeeded with cached 0.13.5.
That audit found zero vulnerabilities or adverse statuses. A reviewed bootstrap
aligns manifest, backend and CI before the existing guarded adapter is applied.
The adapter owns subsequent upgrade resolution and complete verification.

## Starter policy reconciliation

Read the clean released 0.8.0 checkout's changelog, versioning, baseline policy,
updating entry and brownfield runbook. Generated candidates in an empty external
directory, compared old/current/target content, and retained local configuration
additions. Updated the managed fragment, native update skill and coherent
provenance lock. The heavy setting and FDAU operational skill inventory are
unchanged. Project configuration locally disables inherited duplicate sources.

Policy changes require project-only native activation and scope-preserving
updates, latest stable tool review across families, direct Git/GitHub CLIs and
explicit release-specific freshness evidence. Python's host exception remains;
no adopter schedule is imposed. Backplane's future lifecycle ownership does not
replace FDAU's current ROADMAP/BACKLOG/HANDOFF authorities. The starter's own
cognitive exception does not waive FDAU's required UNKNOWN evidence.

## Verification and limitations

Focused pre-change baseline: 55 unittest tests passed on Python 3.12.16.
Final gate results and exact hashes are recorded below.
Local execution receipts live under
`.superpowers/sdd/coordinated-refresh-2026-11-01/`.

The guarded upgrade changed ten locked packages: filelock 4.2.4→4.2.6,
nodeenv 1.11.0→1.12.0, platformdirs 4.13.5→4.14.2, python-dateutil 3.0.0→4.0.0,
python-discovery 1.6.4→1.9.0, Ruff 0.17.2→0.17.3, ty 0.0.92→0.0.95,
tzdata 2026.5→2026.6, virtualenv 21.14.13→21.15.2 and watchdog 6.0.0→7.0.0.
Four retained versions have verified parent constraints: Wily 1.25.0 requires
colorlog `<5`, Plotly `<6` and Radon `<5.2`; Radon 5.1.0 requires mando `<0.7`.
Runtime dependencies remain empty. Other declared tools and CI actions matched
their observed latest stable releases and retain their existing purposes.

### Major transitive compatibility

Reviewed [dateutil 4 notes](https://github.com/dateutil/dateutil/releases/tag/4.0.0)
and [watchdog 7 notes](https://github.com/gorakhargosh/watchdog/releases/tag/v7.0.0).
Both admit Python 3.12. dateutil removes old Python/six compatibility and tightens
malformed numeric ISO parsing. FDAU does not import it at runtime; its installed
ghp-import consumer uses `tzlocal()` in `mk_when()`. The local unittest probe
confirmed fixed/current timestamp generation and timezone-offset shape without
performing a Git publication.

watchdog changes pattern matching and separates attribute events. MkDocs uses
its generic event handler's `on_any_event` with `PollingObserver`, rather than
the changed pattern handler. A real polling probe confirmed nested file-content
and timestamp changes request a rebuild, duplicate watch references unwatch
correctly, and observer shutdown joins cleanly. Both local compatibility tests
passed. These Windows observations do not establish macOS/Linux execution.

### Native and managed content

Codex's scope-preserving marketplace upgrade resolved the actual starter checkout
to `e0b752f`. Native inventory and each component checkout confirmed the full
target SHAs above. A fresh ephemeral, read-only Codex session discovered SP from
the 7.0.1 cache, gz-skills from 0.8.3 and the worktree's native update skill.
The user configuration SHA-256 remained
`29112686b568b2f9f06ae8e08654fa9e95193713912eeb22b3194a31d942cefa`.
An outside-project startup control retained the user's existing Superpowers
discovery and exposed no FDAU-local skill or starter gz-skills source.
Project-only `localize` preview and apply both reported zero writes. Heavy
selection and disabled Backplane are unchanged.

All three generated managed payloads match the released candidates exactly:

| File | SHA-256 |
| --- | --- |
| `AGENTS.skills-first.md` | `4fbedfc45a482d3f6bd9ae3b086099affa1f7ac732dc029e0898781931e4db28` |
| `.skills-first/bundle.lock.json` | `dbce3b4c9f5c64178f34a946d6c2bcc315e873aaf67e9a0e5cdf482064ecfdf6` |
| `.agents/skills/update-gz-template/SKILL.md` | `b4d19a9bd1c91fd3ea7429865354e0065f38bacd89a3693fe15e5b89559b212d` |

The released starter's `status` command still fails on this Windows host with
`duplicate template update skill at .agents/skills`. Its `_check_discovery`
computes `str(Path(...).parent.parent)` with backslashes, then compares it with
forward-slash surface strings. This is a false-positive duplicate, not a second
project skill. No skill was removed or shared helper/cache patched to suppress
the failure. Managed-byte equality, native source and fresh discovery checks
passed independently; helper status remains FAIL and full template acceptance
is not claimed.

### Artifact and provisioning checks

Fresh built-in-catalog provisioning installed Python 3.12.16 into an external
temporary directory using `--no-bin --no-registry`; no shared aliases or registry
entries changed. This verifies removal of the old catalog override.

A fresh wheel/sdist passed strict Twine and exact metadata/inventory checks.
The first offline sdist rebuild exposed an uncached uv_build 0.13.6 backend;
normal online resolution populated that cache, and the repeated offline rebuild
produced a byte-identical wheel:

- Wheel SHA-256: `e1acaf118e8497b66fbc800b1c2174260c1828925a45d420ae3cbf2a39797937`.
- Sdist SHA-256: `3fc655983b55b5a9d5e06ca29102d5dc656a5647ddf6fb6957073347135cdd4b`.

The disposable Python provisioning directory was removed after verification.
The existing development interpreter, shared minor alias, PATH and registry
remain unchanged. External matrix environments were removed by their owning
workflow after successful verification.

### Corrections and independent review

The initial worktree checkout converted historical text to CRLF. Before
continuing past the failed audit, restored only normalized payloads whose Git
blob hashes exactly matched the index, then refreshed unchanged index entries.
No historical semantics, fixture contracts or staged content changed. The first
guarded apply correctly refused a stale digest after byte restoration; a fresh
reviewed digest was used afterward.

uv 0.13.6 renames preview `module_owners` to nested `modules`. A regression
unittest failed on the old parser before the minimal compatibility correction;
both known top-level schemas are explicit and unknown roots remain rejected.
The focused parser suite, Ruff and ty then passed.

The first full hygiene attempt ran 693 tests in 332.798 seconds and found one
failure: this maintenance specification lacked the mandatory exact T2.1/T2.2
acceptance headings. Added those headings without changing their scope; 73
focused governance/dependency/documentation tests passed before the full retry.
The original failed result remains in `apply-final-output.log`. Independent
review found no actionable code defects and accepted the scoped document
correction.

A subsequent attempt passed all 693 tests in 331.545 seconds but pre-commit
rejected its changed diff: the implementer had updated review documentation
while the hook was running. That was an execution mistake, not a test failure.
The candidate was then frozen and the owning complete hygiene gate rerun with
all hooks enabled. No tracked file was edited during the successful final
hygiene and external matrix runs. Failed adapter receipts remain failed; final
verification comes from the separately executed owning gates below.

## Final verification

| Check | Result / evidence |
| --- | --- |
| `uv run --offline --frozen --all-groups python .codex/skills/hygiene/scripts/hygiene.py` | PASS, exit 0; `hygiene-stable.log` |
| All-files pre-commit | Ruff check, format check, ty and unittest all Passed; hooks enabled |
| Strict backlog audit and documentation | PASS within complete hygiene |
| Exact wheel/sdist metadata and inventory | PASS within hygiene and external matrix |
| Existing `tools.dependency_matrix.run_matrix()` | PASS, exit 0; `matrix-result.json` and `matrix.log` |
| External source suite, Python 3.12.16 | 693 unittest tests passed in 363.735 seconds |
| External wheel-only installed smoke | PASS; exact artifact hashes match the independently rebuilt pair above |
| Final `uv lock --check --offline` | PASS, no byte churn; `final-lock-check.json` |
| Final `uv audit --locked --output-format json` | 133 packages, zero vulnerabilities/adverse statuses; `final-advisory.json` |
| Major transitive consumer probes | Two unittest checks passed; `consumer-probe.log` |
| Managed content / native source / fresh discovery | PASS as detailed above |
| Released helper `status` on Windows | FAIL: upstream separator false positive as detailed above |
| Independent scoped change review | No actionable defects; `independent-review.json` |

The unchanged runtime source diff and empty staged diff were checked. The
implementation contains only the intended managed tooling/configuration,
dependency lock, compatibility regression and maintenance documentation changes.
Main remains clean at the rollback HEAD; the temporary worktree and uncommitted
changes are retained pending an explicit integration choice. No push, tag or
release occurred. Closure documentation receives focused governance/docs checks
after this record is finalized; those record-only edits do not alter the tested
source, manifest, lock, native configuration or artifacts.

The completed plan uses the existing historical crosscutting execution-record
family, following the fast-local-closeout precedent. It does not present this
maintenance review as new committed delivery-gate evidence for verified T2.2.

Native configuration, installed revisions and fresh-session discovery are
separate observations. Do not infer any of them from a target ref alone. No user
defaults, global activation, unrelated worktree or embedded host is changed.
Cognitive analysis remains UNKNOWN and existing Lizard acceptance limitations
remain open. No STRICT, whole-stack, simulator-host, integration, Git-sync or
release-completion claim is made.
