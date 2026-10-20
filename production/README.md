# SiderAtlas No.003 — The White Dwarf

One continuous 32-second vertical Reel of six interior gravity modes in a
representative DA / ZZ Ceti white dwarf. The original numerical modes and
version B's slow camera scan are preserved. The frame contains only
**THE WHITE DWARF**, **@sideratlas** and **NO.003**, against black.

The surface colors are a fixed, contrast-enhanced map of the calculated
pulsational temperature departures. They are not the star's visible colors.
Hydrogen-atmosphere spectral emission and limb darkening set the physical
radiance. A normalized virtual optical model creates the soft blue-white
halo without adding a luminous shell or new stellar emission.

The interior adiabatic frequencies are calculated. The excited subset, angular basis,
surface flux amplitudes and phases are prescribed. This is not a reconstruction
of a named star or a fully self-consistent nonadiabatic pulsating atmosphere.

- Film: `output/sideratlas-no003-the-white-dwarf-32s.mp4`
- Caption: `instagram-description.text`
- Convection failure diagnosis and final fallback: [docs/CONVECTION-AUDIT.md](docs/CONVECTION-AUDIT.md)
- Equations, physical scope and imaging: [docs/MODEL.md](docs/MODEL.md)
- Convection, granulation and magnetic decisions: [docs/SURFACE-PHYSICS.md](docs/SURFACE-PHYSICS.md)
- Primary references: [docs/SOURCES.md](docs/SOURCES.md)
- Scientific data credits and terms: [docs/DATA-CREDITS.md](docs/DATA-CREDITS.md)
- Numerical and export reports: `validation/` and `output/render-metadata.json`

The production movie is 1080 × 1920, 30 fps, exactly 960 frames / 32 seconds,
H.264 High / Rec.709 limited / 4:2:0 / fast-start MP4, without audio. It covers
1,721.6 observer seconds at 53.8 times real time. It evolves continuously;
no repeated eight-second clips or forced phase reset are used.

## Final surface decision

Published DA radiation-hydrodynamic models imply granules around 0.85 km wide
at the adopted temperature and gravity. That is only about 0.05 pixel in this
whole-star composition, before diffraction and exposure averaging. Individual
cells cannot be resolved here. Their statistical properties do not specify
a unique global, time-dependent temperature map. No granular texture or
stochastic surface animation was invented.

Magnetic spots have no field strength, geometry, contrast or evolution
calculated for this equilibrium. Magnetic fields can alter both convection
and gravity-mode propagation. The nonmagnetic foundation is retained, without
asserting that spots and pulsations are universally incompatible. The local convection experiment failed its statistical and refinement checks.
Its flow is excluded. The final image retains stronger pulsation contrast
and a normalized halo with 4.5% broad scattering wings. The caption and
[display notes](docs/DISPLAY.md) disclose the fixed false colors, asinh
contrast and added diagnostic luminance gain.

## Reproduction

The portable package keeps the prior physical inputs and rendering components
in their original relative layout. From its top-level directory, install
Python 3.12 with `requirements-research.txt` and FFmpeg with libx264 and zscale:

```sh
python -m pip install -r requirements-research.txt
python production/investigate_surface.py
python production/validate_calculations.py
python production/render_reel.py
python production/calculate_photometry.py
python production/validate_reel.py
```

The saved eigenvalues, eigenfunctions, atmosphere data and cache suffice to
render without GYRE or network access. Unmodified GYRE 9.1.1 is an optional
external dependency for recomputing the interior eigenproblems; the retained
input files, original provenance and convergence checks accompany the source.
The published WDEC equilibrium is reused, not a newly evolved stellar model.

Four-second closed-GOP checkpoints support resumption. They are joined without
re-encoding, repeating or dropping simulation frames. A checksum fingerprint
prevents mixing checkpoints after source, configuration or physical inputs
change. Use a fresh checkpoint directory after such a change. The default
uses two rendering processes; `--workers 1` reduces peak memory use.
The assembler verifies checkpoint hashes, copies them to private temporary
storage and joins them with strict error handling. This avoids file-provider
open timeouts; frame count and duration are checked before replacing the film.

The final false-color map uses ±160 K with 12 K asinh softening and an
explicit diagnostic luminance gain exp(1.8u). Neither changes the six physical
mode amplitudes. The halo redistributes 4.5% of the modeled source light into
broad wings; it adds no stellar emission.

Only one final film is included in the release package. Earlier previews,
comparison panels, optional convection movies, SDKs and compiled solvers are
excluded. Code is MIT; scientific data and fonts retain their recorded credits
and terms. Instagram will apply its own delivery compression.
