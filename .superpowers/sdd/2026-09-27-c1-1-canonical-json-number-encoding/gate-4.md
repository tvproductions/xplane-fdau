# C1.1 gate 4 — Deterministic bytes and SHA-256

- **Child:** `C1.1`
- **Gate:** `4`
- **Kind:** verification
- **Result:** passed
- **Date:** 2026-09-27
- **Subject:** Stable canonical bytes and content digest.

`tests.test_canonical_json` checks that whitespace/property-order variants converge to identical encoded bytes and that SHA-256 of returned `b'{"test.x":1}\n'` is `c7a95602104d7db4d2fca0e277f6e064854c886d32328a57cb4d28ab10467424`. The encoder uses integer/rational binary64 formatting rather than `json.dumps()` float spelling. The fresh external wheel produced `b'{"test.x":1.0}\n'` on Python 3.12.13. Full offline hygiene exited 0 with 554 `unittest` tests, 94% coverage, strict docs, Ruff, ty, pre-commit, strict Twine, and exact wheel/sdist validation.
