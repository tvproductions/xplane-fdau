# C1.5 gate 4

- **Child:** `C1.5`
- **Gate:** `4`
- **Kind:** verification
- **Result:** passed
- **Date:** 2026-11-01
- **Subject:** Operational findings and tolerances cannot enter acquisition quality.

Direct enum construction and contextual validators reject within_tolerance, outside_tolerance, indeterminate, warning, critical and finding, along with invalid casing and unsupported types. The reference guide preserves the operational/acquisition boundary.

Verified implementation: `4b74399991bf1001196f5062070442e96da5ca0b`.
The 56 final focused tests, complete offline hygiene, strict artifacts and
external installed-wheel smoke passed on Python 3.12.16. All 208 verification
inputs remained unchanged. See [completion](completion.md),
[verification identities](verification.json) and [independent review](review.md).