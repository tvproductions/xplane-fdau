# B1.1 gate 4 — Wheel and source-archive identity

- **Child:** `B1.1`
- **Gate:** `4`
- **Kind:** verification
- **Result:** passed
- **Date:** 2026-09-20
- **Subject:** Exact wheel and source-archive package identity.

Fresh wheel xplane_fdau-0.1.0-py3-none-any.whl has package members under xplane_fdau; fresh sdist xplane_fdau-0.1.0.tar.gz has package members under src/xplane_fdau. tools/release.py check-dist accepted exact members, directories, metadata, RECORD, and byte inventories in both the full hygiene gate and external smoke build. Wheel SHA-256: 08d0e3a55a1ab46b7f5f1911ccdda99926d6f87298bd7b0dc160132627282fcb. Sdist SHA-256: 070ad08f5ab20e70305f4dd022db144292e65ceca78ad78b68af4b6cdeb07b20. Both builds produced the same hashes. Task 3's test-first suite passed 26 tests, including rejection of flat sdist and src-prefixed wheel members and existing hostile archive cases. Strict Twine passed.
