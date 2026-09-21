# B1.1 gate 3 — Source and installed import isolation

- **Child:** `B1.1`
- **Gate:** `3`
- **Kind:** verification
- **Result:** passed
- **Date:** 2026-09-20
- **Subject:** Repository-root and installed-wheel import isolation.

The repository-root subprocess test resolves xplane_fdau.__file__ under src/xplane_fdau and rejects a flat package. A fresh wheel was built, validated, and installed offline into an external Python 3.12.13 environment. tools/installed_smoke.py 0.1.0 exited 0 from that directory. Direct import resolved to C:\Users\Jeff\AppData\Local\Temp\xplane-fdau-b1-1-92c39ef60fa34596ac8eacd88f8e39be\smoke\Lib\site-packages\xplane_fdau\__init__.py. The verified temporary directory was removed after success. The full source suite passed 521 unittest tests.
