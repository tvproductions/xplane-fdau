# C1.3 independent review and executor disposition

- **Child:** `C1.3`
- **Gate:** —
- **Kind:** review
- **Result:** accepted
- **Date:** 2026-10-11
- **Subject:** Independent whole-branch review, with both Important findings resolved.

Independent reviewer `/root/c13_review` reviewed `1a993f3753fafcd3a50f720ce7e58fafad42c02a..1c443ea168337c2d8a5b4cca2b9c38438b1b2268` against the approved specification, plan, four gates, and project boundaries. Its focused run passed 70 tests. It reported zero Critical, two Important, and zero Minor findings.

1. The bare omission sentinel changed identity after deepcopy or pickle, exposing a private marker or causing canonical serialization failure. The executor reproduced this with literal-byte reconstruction assertions, then replaced the marker with a private Enum singleton.
2. Constructors and wire readers traversed irrelevant variant properties in different shape order. A null element tag could also be deferred beyond a later shape error. The executor reproduced the differing paths and aligned both paths with the full semantic field inventory.

Both findings are fixed in `0b25c7c6a46791aaae94b08ba5c18a3c8bfe79b0`. The reconstruction and mixed-invalid regression methods fail on the reviewed implementation and pass on the corrected implementation. A separate reconstruction negative control covers deepcopy and pickle. The final focused run passed 88 tests; Ruff lint/format, ty, and affected Xenon checks passed. This accepted disposition combines the independent findings with executor verification; no second independent review is claimed.

The review excludes concurrent caller mutation, the broader pre-existing weak-test audit, and later simulator/catalog/family integration. Ordinary caller mutation after construction is covered. The scope rulings and their costs are recorded in `progress.md`.
