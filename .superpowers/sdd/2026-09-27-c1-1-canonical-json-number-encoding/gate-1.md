# C1.1 gate 1 — Exact canonical JSON bytes

- **Child:** `C1.1`
- **Gate:** `1`
- **Kind:** verification
- **Result:** passed
- **Date:** 2026-09-27
- **Subject:** UTF-8, Unicode, object-key and array order, escaping, and final LF.

`tests.test_canonical_json` asserts Unicode scalar key ordering, preserved array order, UTF-8 output, exact control/quote/backslash escaping, NFC and surrogate handling, and exactly one final LF. It also checks parameter/document depth and 65,535/65,536 member boundaries. The complete offline hygiene gate exited 0 with 554 `unittest` tests and 94% coverage. The fresh wheel passed strict inventory and installed smoke on Python 3.12.13.
