# C1.4 completion

- **Child:** `C1.4`
- **Gate:** —
- **Kind:** verification
- **Result:** passed
- **Date:** 2026-10-26
- **Subject:** Immutable clock domains/readings, exact UTC, anchors and explicit source/simulator timing.

The four C1.4 gates are satisfied by the delivered timing models, closed
vocabularies, checked arithmetic, strict private nested readers, explicit
canonical dispatch, public re-exports, runnable documentation and installed
smoke. Runtime remains standard-library-only and Python 3.12-only. No clock
sampling, scheduling, registry, adapter, family loader/schema or later record
model was introduced. Acquisition phase stays a closed string; enclosing-record
producer integration remains C3.1.

Verified baseline: `a2ef12d411d20017b7099eb6d97f3a12b6c5e4f4`.
Verified source: HEAD `5448aef4804e69b60a448f0612c3ddba8c122cb3` plus staged
tree `e97f887d9e8deab63cf331148b1fbd73dbb9259f`, containing the final task and
review correction. `stable-inputs.json` records 130 exact source/test/tool/build/
documentation input hashes; every hash matched after both complete checks.
Subsequent plan, backlog and evidence edits do not change those inputs.

Observed verification:

- 92 focused feature/public/documentation/import tests passed. Ruff check,
  Ruff format --check, ty and all three Import Linter contracts passed.
- `uv run --offline --locked --all-groups mkdocs build --strict` passed,
  including the rendered timing API and executable documentation examples.
- `uv run --offline --frozen --all-groups python .codex/skills/hygiene/scripts/hygiene.py`
  exited 0: lock/backlog/docs, all-files mandatory Ruff/format/ty/unittest hooks,
  and a fresh external wheel/sdist with strict metadata/inventory validation.
- The approved `tools.dependency_matrix.run_matrix(Path.cwd())` procedure,
  launched through offline locked all-group uv with `UV_OFFLINE=1`, exited 0.
  Its isolated Python 3.12.16 source environment passed **691 unittest tests in
  307.496 seconds**. Its separate wheel-only Python 3.12.16 environment passed
  installed smoke and enforced package import origin outside the checkout.
  Every recorded matrix command exited 0; no failure path was preserved.

The external matrix's exact artifacts:

| Artifact | SHA-256 |
| --- | --- |
| `xplane_fdau-0.1.0-py3-none-any.whl` | `f244f18648aff6a686762aae1eb5a69200fb2eb517102f1878bd4790abac5f5d` |
| `xplane_fdau-0.1.0.tar.gz` | `a6de6b6d582944b42672565e897a706d4fe5472c2a254b599e4137467f9a514f` |

Hygiene safely removed its successful external directory
`C:/Users/Jeff/AppData/Local/Temp/xplane-fdau-hygiene-u5degpjd`.
The successful matrix likewise removed
`C:/Users/Jeff/AppData/Local/Temp/xplane-fdau-matrix-y6ms2xbh` and its environments.
Raw command logs/result JSON are local-only execution evidence; durable gate,
review, manifest and progress receipts are retained here. Hardlink-to-copy
fallback and the existing MkDocs Material migration notice were informational.

Independent review reported one Important semantic-order defect; an assertion-
level RED-to-GREEN fix and the full green suite resolved it. No Critical,
Important or Minor finding remains within C1.4. See `review.md` and `progress.md`
for review scope and all executor decisions/costs. No second review is claimed.

Jeff authorized inline execution, local checkpoints and the bounded installed
Superpowers 7.0.1 source exception after its shared cache changed externally.
Shared bundle adoption and deferred cognitive analysis remain separate;
starter STRICT acceptance and G1 remain incomplete. This bounded completion
does not authorize remote sync, local integration, tags, publication or release.
