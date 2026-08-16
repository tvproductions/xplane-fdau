# xplane-fdau

`xplane-fdau` is the standard-library-only, transport-free flight-data kernel
for X-Plane. External XPPython3/XPLM and `xplane-webapi` clients use its ports
and domain behavior, but this project never connects to X-Plane itself. It is
provider-neutral among X-Plane access paths, not simulator-neutral.

Version `0.1.0` is unreleased and has no runtime dependencies. The tested
compatibility range is Python 3.12 through 3.14. Python 3.12 is the core's
minimum syntax and API discipline so it can be composed into a compatible
XPPython3 client; an exact embedded-interpreter pin belongs to that client.
The project does not import a Web API client, XPPython3, `xp`, or XPLM.

## Core boundary

The core owns canonical FDAU semantics and artifacts, recording, recovery,
replay, native X-Plane FDR support, edition-pinned ARINC profiles and codecs,
and X-Plane FDM/FOQA-oriented analysis. ARINC and analysis capabilities are
roadmap work and are not all present in the unreleased `0.1.0` surface.

External clients own every concrete path into or out of X-Plane: DataRefs,
XPLM callbacks, plugin lifecycle, Web API transport, connections, discovery,
and scheduling. Both q4xpcc and clients built on `xplane-webapi` can therefore
share one standard-library implementation of the domain and standards rules.

## Native FDR boundary

Native FDR parsing, models, deterministic canonical v4 writing, profiles,
configuration, validation, and GeoJSON projection live in
`xplane_fdau.formats.xplane_fdr`. Push-first publication lives in
`xplane_fdau.sinks.xplane_fdr`. The native format is not a canonical FDAU
recording model or archive.

The client adapter owns acquisition transport: it reads simulator values,
chooses cadence scheduling, manages connections and plugin lifecycle, and
submits observations through core ports. Capture adapters are not bundled.

## Offline native FDR commands

```powershell
xplane-fdau fdr inspect flight.fdr
xplane-fdau fdr validate flight.fdr
xplane-fdau fdr to-geojson flight.fdr flight.geojson
```

The command line does not include a live-record command. Native X-Plane
textual `.fdr` v3/v4 files are not ARINC recorder/QAR formats. Future
standards and analysis modules will remain distinct from this native format,
and library analysis will not itself establish an approved FOQA program or its
organizational thresholds and protections.

Continue with the [native FDR guide](usage/native-fdr.md) or the
[native FDR API reference](reference/native-fdr.md). The
[core-scope amendment](architecture/xplane_fdau_core_scope_amendment.md)
defines the governing ecosystem boundary.
