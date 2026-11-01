# C1.5 completion and verification

- **Child:** `C1.5`
- **Gate:** —
- **Kind:** verification
- **Result:** passed
- **Date:** 2026-11-01
- **Subject:** Validity and acquisition-quality vocabulary delivered and verified.

The approved native execution delivered public `ValidityState` and
`QualityFlag` in `xplane_fdau.measurements.models` and its owning package,
private strict scalar/array-set validators, contextual rejection tests,
installed smoke and a rendered reference guide. The complete sample matrix,
catalog authorization, lineage, family loaders and schemas remain their
approved later slices. Root exports and the stdlib-only runtime are preserved.

## Candidate and evidence identity

Reviewed and fully verified implementation:
`4b74399991bf1001196f5062070442e96da5ca0b`, based on
`82b1e81a42eab27c47037bc1dc47c4b4378b9476`.
Task commits are `8aca300`, `8ce60af`, and `4b74399`.
[inputs.json](inputs.json) binds all 208 unchanged tracked source, test, tool,
policy and documentation inputs; it excludes delivery-state/evidence files and
this implementation plan so later evidence bookkeeping is explicit.
[verification.json](verification.json) records checked hashes and environment.

Python 3.12.16 is the sole execution minor. Unittest discovery contained 709
tests; every task commit passed the complete mandatory unittest hook. The final
56 focused feature/API/smoke/import/documentation tests passed. Final Ruff lint,
format and ty passed, as did strict MkDocs. No hook was skipped or bypassed.

The exact complete closeout command passed:

```powershell
uv run --offline --frozen --all-groups python .codex/skills/hygiene/scripts/hygiene.py
```

This covered frozen lock consistency, backlog audit, strict documentation,
all-files pre-commit (Ruff, formatting, ty, full unittest), one fresh external
sdist/wheel build, strict metadata, exact archive inventory and safe artifact
cleanup. No second standalone quality aggregate was run on this candidate.

## Installed artifacts

The externally built and independently installed artifact pair has these hashes:

- Wheel `xplane_fdau-0.1.0-py3-none-any.whl`:
  `d6eaa482565cecdd47990d8df463da8026978f5912761edc0697f77ee02c0ac1`.
- Sdist `xplane_fdau-0.1.0.tar.gz`:
  `bfe6b1456e7a48a9add03e2fddada7a310f920ef02b6c6e3477e462a91f45244`.

The full hygiene build produced byte-identical wheel and sdist hashes. Its
owned temporary pair was removed by the existing hygiene cleanup; the matching
external smoke pair was retained under the path in `verification.json`.
The wheel was built from the sdist by `uv build --offline --no-sources`,
passed strict Twine and release-inventory checks, and was installed with
`uv pip install --offline --no-deps` in a new external Python 3.12.16 environment.
The existing `tools/installed_smoke.py 0.1.0` passed there through
`uv run --offline --no-project --python <external interpreter>`.
Import origin was that environment's site-packages and runtime requirements
were empty. Windows was observed; no additional Python minor matrix is claimed.

## Review and corrections

[Independent review](review.md) accepted the whole branch with zero Critical,
Important or Minor findings. It was a static independent review: the reviewer's
sandbox prevented its attempted uv checks, and executor logs supply execution
proof. No correction pass was needed after review.

The initial Task 1 full hook failed with 32 failures and 3 errors: the synthetic
release fixtures lacked the new measurements directory, and native checkout
CRLF endings changed provenance-locked document bytes. Focused reproductions
identified both causes. The fixture directories were corrected, and only
proven CRLF-only differences were restored to exact indexed bytes, preserving
intentional byte fixtures. The next full hook passed. The runtime release
validator, provenance hashes, thresholds and mandatory hooks were unchanged.
The approved plan and execution ledger record the bounded inventory/export
order refinements; the sixteenth-item test still rejects at `/quality/15`.

Raw RED/GREEN, hook, hygiene and review-package logs are retained as local-only
execution evidence under this receipt directory's `execution/` subdirectory.
They are not available from a fresh clone; the committed receipts and hashes
are the durable summary.

C1.5 acceptance does not establish STRICT starter conformance, G1, a release,
remote synchronization or local integration. Those authorities remain separate.