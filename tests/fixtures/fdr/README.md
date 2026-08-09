# FDR Fixture Provenance

These fixtures are independently minimized, synthetic test artifacts. They
retain only the format facts needed by the reader and writer tests; no complete
Laminar Research recording or real flight sample is copied here.

## Installed Laminar Research evidence

The licensed installation used for verification identifies itself in
`X:\X-Plane 12\Log.txt` as X-Plane `12.4.3-r2-15ff1e4d`, build `124311`.
The installed sources inspected on 2026-08-09 were:

- `X:\X-Plane 12\Instructions\FDR Example Version 3.fdr`
  (SHA-256 `127F1D2357991DDD64381F1F2A2E8FD4D3E02FAD5FE9FB353933EE0D41A797AD`)
- `X:\X-Plane 12\Instructions\FDR Example Version 4.fdr`
  (SHA-256 `1E49CAE91FD0918FEE9605889666FC11E37B95627D045B123F552DB83CEDA422`)
- `X:\X-Plane 12\Instructions\FDR files in X-Plane.rtf`
  (SHA-256 `978FA0CED016A0CD70D40108B91A2E2A729CC3B35A348F49728A0CEE5196424D`)

The RTF directs readers to the example files for their inline format
explanations. In the v3 example, `COMM` lines 20-23 document the row semantics
and `COMM` line 78 names every column. Its first two header lines are exactly:

```text
A
3 This is the needed beginning of the file: 'A' or 'I' for 'Apple' or 'IBM' carriage-returns, followed by an IMMEDIATE carriage return, followed by the version number of 3 for the v3 format, or 4 for the v4 format
```

The official v3 file contains 108 CRLF-terminated lines. Its record kinds are
`COMM`, `ACFT`, `TAIL`, `TIME`, `DATE`, `PRES`, `DISA`, `WIND`, `WARN`,
`DREF`, and `DATA`, in addition to the origin and version lines. All 30 `DATA`
rows contain exactly 41 values after the `DATA` label. Zero-based indices in
that 41-value row are:

| Index | Meaning |
| ---: | --- |
| 0 | elapsed seconds from the `TIME` start |
| 1 | longitude in degrees |
| 2 | latitude in degrees |
| 3 | altitude MSL in feet |
| 4 | magnetic heading in degrees |
| 5 | pitch in degrees |
| 6 | roll in degrees |

The verified complete v3 field order is: `time`, `Longitude`, `Latitude`,
`Altitude`, `HDG`, `Pitch`, `Roll`, `BaroA`, `AltMSL`, `VSpd`, `TAS`, `IAS`,
`GndSpd`, `Stall Warning`, `flap`, `flap`, `OAT`, `wind`, `wind speed`,
`FQtyL`, `FQtyR`, `volt1`, `amp1`, `OilP`, `OilT`, `Eng1 Percent Power`,
`RPM`, `MAP`, `FFlow`, `CHT-1`, `CHT-2`, `CHT-3`, `CHT-4`, `CHT-5`,
`CHT-6`, `EGT-1`, `EGT-2`, `EGT-3`, `EGT-4`, `EGT-5`, `EGT-6`.
The example has 29 `DREF` records but 34 post-navigation values because its
column documentation expands the CHT and EGT arrays. That is why v3 rows are
treated as the verified fixed legacy layout rather than inferred from v4.

## Synthetic fixture shapes

- `version3-minimal.fdr` preserves the official `A`/`3` header, CRLF line
  endings, two 41-value `DATA` rows, and the exact legacy field order. Every
  sample number and identifying metadata value is synthetic.
- `version4-minimal.fdr` follows the installed v4 LF shape, has the exact
  `A\n4\n` prefix, two Chicago-area samples, and one synthetic `DREF` with a
  `2.0` conversion factor and a comment.
- `inherited-recorder-minimal.fdr` preserves the valid Windows text-mode shape
  of the former `xpwebapi` demonstration recorder at commit
  `bd8dadde8dabdda681ad8c3bd10420f807f063ed`, source `examples/fdr.py`.
  Its `print("A\\r4\\n", file=fp)` produced a bare CR after `A`, CRLF for the
  remaining lines, comma-space sample separators, and the header form
  `DREF, path  2.0 // comment: text`. Values and metadata are synthetic.
