# C1.5 gate 2

- **Child:** `C1.5`
- **Gate:** `2`
- **Kind:** verification
- **Result:** passed
- **Date:** 2026-11-01
- **Subject:** Quality flags are closed, unique, and lexically ordered.

All fifteen exact flag spellings and immutable owned results are pinned. Tests reject duplicate and noncanonical inputs, exercise all 105 reversed unique pairs, preserve caller input, and reject the sixteenth duplicate with ContractValidationError at /quality/15.

Verified implementation: `4b74399991bf1001196f5062070442e96da5ca0b`.
The 56 final focused tests, complete offline hygiene, strict artifacts and
external installed-wheel smoke passed on Python 3.12.16. All 208 verification
inputs remained unchanged. See [completion](completion.md),
[verification identities](verification.json) and [independent review](review.md).