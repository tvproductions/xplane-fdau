# FDR toolkit guide

## Read native FDR files

`FDRReader` accepts native X-Plane FDR v3 and v4 files. It preserves the
source version and exposes a common navigation view; a v3 file is never
silently rewritten.

```python
from xplane_fdr import FDRReader

recording = FDRReader().read("Input/FDR files/flight.fdr")
print(recording.header.source_version)  # 3 or 4
```

## Write canonical v4

`FDRWriter` always emits canonical v4 UTF-8/LF text. A v3 source can be
normalized only through an explicit opt-in because its legacy fields may be
omitted. Treat this conversion as lossy and examine the reported omissions.

```python
from xplane_fdr import FDRReader, FDRWriter

legacy = FDRReader().read("legacy-v3.fdr")
result = FDRWriter().write(
    legacy,
    "normalized-v4.fdr",
    allow_lossy_legacy=True,  # explicit opt-in
)
print(result.omitted_legacy_field_ids)
```

For an already-v4 recording, no opt-in is needed:

```python
recording = FDRReader().read("flight-v4.fdr")
FDRWriter().write(recording, "canonical-v4.fdr")
```

## Record from an adapter

Recording is push-first. The adapter owns capture, cadence scheduling,
connections, and plugin lifecycle; the callback constructs a semantic
`FDRSample` and calls `session.record(sample)`. No capture adapters are
bundled, and the library never starts a background thread or connection.

```python
from datetime import time
from pathlib import Path
from xplane_fdr import (
    FDRHeader,
    FDRRecordingDefinition,
    FDRRecordingSession,
    FDRSample,
    FDRSamplingPolicy,
    FDRStoragePolicy,
)

definition = FDRRecordingDefinition(
    header=FDRHeader(4, "A", (), (), (), (), None),
    sampling=FDRSamplingPolicy(interval_seconds=1.0),
    storage=FDRStoragePolicy(directory=Path("Output/FDR files")),
)
sample = FDRSample(time(12), -87.9, 41.9, 700, 270, 2, -1, (), ())

with FDRRecordingSession.open("flight.fdr", definition) as session:
    # Call from the adapter's chosen callback or loop.
    session.record(sample)
```

The pull convenience builds on the same session for an adapter-owned iterable:

```python
with FDRRecordingSession.open("flight.fdr", definition) as session:
    sample_count = session.record_from((sample,))
```

Path-based recording writes a uniquely named sibling partial first. Before
publication, a failure retains the partial for diagnosis and never creates the
requested final artifact. After publication, the final path is already linked
and committed. If removing the partial then fails, the library raises a
cleanup-specific `FDROutputError` and retains both the final artifact and the
partial artifact. Callers must not blindly retry publication after that error;
they should inspect the final and partial paths first. Existing destinations
are protected unless `overwrite=True` is supplied explicitly.

## Configure profiles, custom DataRefs, and storage

Load a strict JSON configuration, then resolve its version-4 recording
definition. The reusable configuration is adapter-neutral: it contains no
connection settings, callback settings, or overwrite permission.

```json
{
  "$schema": "https://tvproductions.github.io/xplane-fdr/schemas/fdr-record-config-v1.schema.json",
  "schema_version": 1,
  "profiles": ["standard"],
  "datarefs": [
    {
      "path": "sim/cockpit2/engine/indicators/EGT_deg_C[0]",
      "comment": "engine one EGT"
    }
  ],
  "storage": {
    "directory": "Output/FDR files",
    "filename": "training-flight.fdr"
  }
}
```

Custom DataRefs extend or override profile declarations in order. The complete
contract is the packaged
[fdr-record-config-v1.schema.json](https://github.com/tvproductions/xplane-fdr/blob/main/xplane_fdr/schemas/fdr-record-config-v1.schema.json).

```python
from xplane_fdr import FDRRecordingSession, load_record_config, resolve_recording_definition

config = load_record_config("recording.json")
definition = resolve_recording_definition(config)
session = FDRRecordingSession.open(
    None,
    definition,
    xplane_root="C:/X-Plane 12",
    filename="caller-choice.fdr",
)
```

`Output/FDR files` is the default directory and is relative to the X-Plane root
provided by the adapter. An absolute configured directory needs no root. A
complete destination path wins; otherwise a caller filename wins over the
configured filename. If neither supplies a name, the library generates a UTC
name such as `xplane-fdr-YYYYMMDDTHHMMSSffffffZ.fdr`.

## Convert to GeoJSON

```python
from datetime import date
from xplane_fdr import FDRReader, recording_to_geojson

recording = FDRReader().read("flight.fdr")
feature_collection = recording_to_geojson(recording, first_utc_date=date(2026, 8, 8))
```

GeoJSON positions are 2D `[longitude, latitude]`. FDR altitude is MSL, whose
meaning is not implied by GeoJSON's optional third coordinate, so it appears in
properties as `altitude_msl_ft` and an explicit metre conversion instead.

## Offline commands

The standalone CLI provides only offline file operations:

```powershell
xplane-fdr inspect flight.fdr
xplane-fdr validate flight.fdr
xplane-fdr to-geojson flight.fdr flight.geojson --first-utc-date 2026-08-08
```

It does not include a live-record command. A capture adapter may offer its own
user interface or command while using this library's session API.

## XPPython3 installation

Install the released wheel into XPPython3's supported Python environment using
its supported pip facilities, and pin or bound the compatible package version
in the consuming project. A consumer plugin constructs samples and submits them
from its chosen flight-loop callback; this library does not bundle simulator
integration or invoke an installer itself.
