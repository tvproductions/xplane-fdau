# xplane-fdau

`xplane-fdau` is a standard library-only virtual Flight Data Acquisition Unit /
Flight Data Interface Unit toolkit for X-Plane. Native X-Plane FDR v3/v4 is
retained as one deliberately lossy replay format and recording sink; it is not
the canonical FDAU archive.

Version `0.1.0` is unreleased. Python 3.12 or newer is required. The project
does not import a Web API client, XPPython3, `xp`, or XPLM.

## Native FDR boundary

Native FDR parsing, models, deterministic canonical v4 writing, profiles,
configuration, validation, and GeoJSON projection live in
`xplane_fdau.formats.xplane_fdr`. Push-first publication lives in
`xplane_fdau.sinks.xplane_fdr`. The native format is not a canonical FDAU
recording model or archive.

The adapter owns acquisition: it reads simulator or external values, chooses
cadence scheduling, manages connections and plugin lifecycle, and submits
native semantic samples. The capture adapters are not bundled.

## Offline native FDR commands

```powershell
xplane-fdau fdr inspect flight.fdr
xplane-fdau fdr validate flight.fdr
xplane-fdau fdr to-geojson flight.fdr flight.geojson
```

The command line does not include a live-record command. Native X-Plane
textual `.fdr` v3/v4 files are not real-aircraft ARINC recorder/QAR formats,
and this project does not provide FOQA/FDM analytics or program thresholds.

Continue with the [native FDR guide](usage/native-fdr.md) or the
[native FDR API reference](reference/native-fdr.md).
