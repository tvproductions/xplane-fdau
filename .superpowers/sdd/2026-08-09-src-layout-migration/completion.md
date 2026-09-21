# B1.1 source-layout migration completion

- **Child:** `B1.1`
- **Gate:** —
- **Kind:** verification
- **Result:** passed
- **Date:** 2026-09-20
- **Subject:** B1.1 source-layout migration completion.

The complete 17-file runtime package moved byte-for-byte to src/xplane_fdau with uv_build module-root "src". Imports and wheel members remain xplane_fdau; sdist members carry src/xplane_fdau. Quality, documentation, and artifact checks use the physical source path. Test-first implementation commits are 3c98306, 04a4ed8, and f2f720f. Stable-closeout corrections are c96d205 (live active-child status assertion) and 179af58 (generated secrets baseline). No runtime package bytes changed.

The clean candidate passed full offline hygiene: 521 unittest tests, 43.9% coverage, Ruff, ty, strict MkDocs, pre-commit, strict Twine, and exact wheel/sdist validation. External Python 3.12.13 wheel installation and smoke passed. Wheel SHA-256: 08d0e3a55a1ab46b7f5f1911ccdda99926d6f87298bd7b0dc160132627282fcb. Sdist SHA-256: 070ad08f5ab20e70305f4dd022db144292e65ceca78ad78b68af4b6cdeb07b20. Independent review accepted the implementation with no findings. Gate receipts 1–5 provide acceptance evidence. B1.1 remains unreleased; C1.1 is the next canonical child.
