# xplane-fdr

A standard-library-only Python toolkit for reading, writing, recording,
validating, and converting native X-Plane Flight Data Recorder (`.fdr`) files,
independent of how flight data is captured.

`xplane-fdr` supports Python 3.12+ and has no runtime dependencies. It reads
X-Plane FDR v3 and v4 input, and writes deterministic canonical FDR v4 output.
Capture remains adapter-owned: this package does not bundle Web API or XPLM
adapters, connections, cadence scheduling, or plugin lifecycle management.

```powershell
python -m pip install xplane-fdr
```

See the [documentation site](https://tvproductions.github.io/xplane-fdr/) for
the [toolkit guide](docs/usage/fdr-toolkit.md) and
[stable API reference](docs/reference/fdr.md).
