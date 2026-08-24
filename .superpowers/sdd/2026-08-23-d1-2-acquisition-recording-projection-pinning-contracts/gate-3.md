# Verification Evidence

- **Child:** `D1.2`
- **Gate:** `3`
- **Kind:** verification
- **Result:** passed
- **Date:** 2026-08-23
- **Subject:** Reproducible deployment pinning and no-divergent-subset proof

The approved design fixes two deployment modes: `installed_wheel` and
`reproducibly_bundled`. Both start from a consumer-trusted
`ExpectedDeploymentPin` obtained independently of the candidate artifact.
That pin carries exact distribution identity, repository revision,
release-wheel filename/media type/length/SHA-256, wheel `METADATA` and `WHEEL`
member lengths and hashes, and the conformance-manifest path, length, and
hash.

After the whole wheel matches its trusted pin, verification checks exact
mode-specific metadata, supported Python, empty `Requires-Dist`, the complete
`xplane_fdau/**` inventory derived from the verified wheel, every delivered
file length and SHA-256, absence of extra non-cache files, a single verified
import root, the pinned conformance manifest, conformance exit status, and
canonical result bytes. A reproducible bundle delivers that identical package
inventory without copying the wheel's `.dist-info` tree; its metadata proof
still uses the pinned wheel members.

The ordered, fail-collecting procedure rejects missing, changed, or additional
delivered files and therefore proves no divergent subset can pass. A pin
mismatch prevents wheel-derived metadata or inventory from becoming trusted.
The design fixes these shapes and rules without inventing a current version,
source revision, filename, artifact hash, delivered-file hash, receipt,
release, or deployment claim.
