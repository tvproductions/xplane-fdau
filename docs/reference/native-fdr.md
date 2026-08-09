# Native X-Plane FDR API reference

Native FDR parsing, models, writing, profiles, configuration, validation, and
GeoJSON projection are supported through
`xplane_fdau.formats.xplane_fdr`. The native recording sink and its definition
types are supported through `xplane_fdau.sinks.xplane_fdr`. These interfaces
are for the deliberately lossy native FDR projection, not a canonical FDAU
archive.

```python
from xplane_fdau.formats.xplane_fdr import FDRReader, FDRWriter
from xplane_fdau.sinks.xplane_fdr import FDRRecordingSession
```

::: xplane_fdau.formats.xplane_fdr
    options:
      show_source: false
      members_order: source

::: xplane_fdau.sinks.xplane_fdr
    options:
      show_source: false
      members_order: source
