# C1.1 gate 3 — Typed rejection and context

- **Child:** `C1.1`
- **Gate:** `3`
- **Kind:** verification
- **Result:** passed
- **Date:** 2026-09-27
- **Subject:** Duplicate keys, invalid text, overflow, and nonfinite values.

`tests.test_contract_json_parse`, `tests.test_canonical_json`, and `tests.test_contract_binary64` assert escaped duplicate-key rejection before numeric-domain errors; JSON Pointer paths including `~` and `/` escapes; malformed UTF-8/BOM and syntax context; non-NFC/lone-surrogate rejection; Int64 and real overflow; nonzero underflow; and NaN/infinity rejection with nested paths. Review-found context and precedence defects were reproduced red, fixed in `a39c326`, and accepted on re-review. Full offline hygiene exited 0.
