# SDD ledger — plan: docs/superpowers/plans/2026-09-27-c1-1-canonical-json-number-encoding.md
Baseline: cba17ec67e458db5a007a19f8c7b0885e53e46fa; isolated worktree feature/c1-1-canonical-json; 9 focused baseline tests pass.
Pre-flight: Task 1 produces _parse_json_document/_NumberToken/_materialize_number and errors consumed by Task 2; names and signatures align.
Pre-flight: Task 2 produces canonical_bytes/_encode_document consumed by Tasks 3 and 4; Task 3 adds _binary64 integration; Task 4 consumes both; interfaces align.
Task 0: Ruling: change plan status to in_progress before backlog planned→in_progress — backlog lifecycle requires matching plan status; cost if wrong: governance transition requires correction.
Task 1: complete (commit 3265ad7; 17 focused unittest tests pass; Ruff check/format and ty pass; RED duplicate/token assertions observed).
Task 2: complete (commit 80bc513; 27 focused unittest tests pass; Ruff check/format and ty pass; RED byte/depth/validation assertions observed).
Task 3: complete (commit a786e18; 31 focused unittest tests pass incl. 4096 unique V8 oracle rows and all finite exponents; Ruff check/format and ty pass; RED RFC vector observed).
Oracle: Node/V8 v24.19.0 JSON.stringify(Number); tests/data/c1_1_binary64_oracle.tsv SHA-256 669cf361937c1fccc4a87dcc89047fdaa34cf0ac5d0b7f0916a996c2b01dd1ac.
Final review: Important exact-zero exponent underflow fixed; unittest RED→GREEN. Important numeric subclass emission fixed; unittest RED→GREEN. Important canonical property validation order fixed; unittest RED→GREEN. Reviewer Minor UTF-8 coordinates regraded Important against exact-context spec and fixed; unittest RED→GREEN. Focused 43/43 tests, Ruff check/format, ty pass. Commit a39c326.
Task 4: integration and installed-smoke assertions complete (commit aa7f5a1); the smoke fault-injection assertion failed before implementation and passed afterward.
Quality-gate repair: detect-secrets baseline classified exactly nine reviewed test vectors (commit 2e9b4f9); Xenon exposed encoder complexity, then behavior-preserving helper extraction passed focused unittest, Ruff, ty, and Xenon (commit 8dfda09).
Independent re-review: accepted through 8dfda09; no remaining Critical or Important findings. Review receipt: review.md.
Release/governance fixture repair: complete gate exposed missing contracts directory entries in synthetic artifacts and C1.1 draft-only assertions; 51 focused tests, Ruff, and ty passed; commit 16198ad.
Complete offline hygiene: exited 0 on corrected candidate; 554 unittest tests, 94% coverage, strict docs/pre-commit, Ruff, ty, complexity, lock, backlog audit, fresh wheel/sdist, strict Twine, exact inventory.
External installed wheel: Python 3.12.13 smoke passed; artifact directory C:\Users\Jeff\AppData\Local\Temp\xplane-fdau-c1-1-6cddc199653a482882ad6a8313f21995; wheel SHA-256 a78b7046a98791946d297b92d8f379aafbff034df5009abd464b704352f2f541; sdist SHA-256 06e78b7c0d089af3fd5743a27c7aaa56cba98a610900aa775e309a7601c6daef.
