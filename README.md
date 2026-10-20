# SiderAtlas NO.003 — THE WHITE DWARF v2.2

One continuous 32-second scientific visualization of a representative ZZ Ceti
white dwarf: six preserved GYRE interior gravity modes, stronger fixed
false-color pulsation contrast, an explicitly magnified statistical convection
layer and luminous optical imaging. Only THE WHITE DWARF, @sideratlas and NO.003
appear in the film. This is not a telescope image or a validated 3D RHD model.

[Final Reel](https://github.com/Loganpis/sideratlas-white-dwarf/releases/download/v2.2.0/sideratlas-no003-the-white-dwarf-32s.mp4) · [Caption](instagram-description.text) · [Reproducible package](https://github.com/Loganpis/sideratlas-white-dwarf/releases/download/v2.2.0/sideratlas-white-dwarf-v2.2.0.zip)

<img src="assets/cover.png" alt="Enhanced mode temperature patterns and magnified cellular convection with a blue-white optical halo" width="360">

## Scientific boundaries

**Calculated:** WDEC-based structure, six adiabatic GYRE eigenfrequencies,
surface flux harmonics under prescribed excitation, DA spectral radiation,
limb darkening, weak-field photon propagation and a separate fixed-observer
physical-mode light curve.

**Approximated:** finite-lived weighted Voronoi granulation matched to neighboring
published DA bolometric contrast and approximate lifetime statistics. Cell
morphology, drift and birth process are prescribed; no fluid velocity, new RHD
solution or validated mode–convection coupling is claimed. Failed local-flow
outputs are not used. Granules are enlarged about 551x to be visible.

**Enhanced:** fixed +/-160 K false colors, asinh softening 4 K, pulsation
log-luminance gain 2.7, cellular contrast exponent 4, prescribed optical PSF and
sixfold halo display gain. Mode time advances 53.8x faster; convection advances
20x slower. These deliberately separate display clocks do not represent
simultaneous physical evolution.

See [physical model](v220/docs/MODEL.md), [convection approximation](v220/docs/CONVECTION.md),
[display equations](v220/docs/DISPLAY.md), [primary sources](v220/docs/SOURCES.md)
and [data credits](v220/docs/DATA-CREDITS.md).

## Reproduce

Use Python 3.12 with the versions in requirements-lock.txt and an FFmpeg build
with libx264 and zscale. Saved stellar, atmosphere, font and cellular inputs are
included; building GYRE is unnecessary to render the film. Original GYRE inputs
and numerical reports are retained for auditing the interior calculation.

```sh
python v220/validate_cells.py
python v220/render_reel.py --workers 2
python v220/validate_reel.py
python v220/package_release.py
python v220/reproduce_package.py
```

The cellular catalog and calibration are included. `calibrate_cells.py`
recomputes fitted statistics if needed; it is not necessary before rendering.
No network access, failed convection experiment or arbitrary texture image is
needed. The render is deterministic from saved inputs; closed-GOP checkpoints
allow resumption without repeating completed chunks. Input fingerprints prevent
mixing results from different configurations. Reproduction checks a freshly
extracted frame against the source image hash and input fingerprint.

## Layout

- `src/`, `data/`, `calculations/`: preserved structure, atmosphere and mode inputs
- `luminous/src/`: normalized polychromatic optical model
- `v220/`: current renderer, cellular model, configuration, caption and documentation
- `v220/validation/`: statistical, numerical, final export and reproduction checks
- `v220/output/`: physical observer curve, camera schedule and render provenance
- Release assets: one final MP4, caption `.text`, source/data ZIP and checksums

The short local preview precedes the final export; alternative movies,
experimental flow solvers, raw rejected snapshots and compiled SDKs are excluded
from the release. Earlier published work remains accessible through Git tags.
Original code is MIT; external data and fonts retain their individual terms.

The root `render_previews.py` supplies the preserved renderer factory used by
the current pipeline. `v220/render_reel.py` is the current film entry point.
