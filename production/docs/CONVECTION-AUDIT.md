# Convection investigation and final inclusion decision

The final film follows the user's authorized fallback: retain the six GYRE
modes and improved luminous imaging, exclude visible granulation if local
RHD validation fails. No convective cells are enlarged. No procedural texture,
stochastic global flicker, separate granulation clock or new temperature
field is added. This decision does not assert that a real ZZ Ceti atmosphere
lacks convection.

## Physical constraints

The retained neighbor-model interpolation from Tremblay et al. (2013b,
Table 1) estimates a characteristic scale of 0.85 km, bolometric vertical
intensity RMS of 17%, and photospheric Mach number of 0.65. The corresponding
7–9 km/s estimate is conditional on an assumed adiabatic exponent; it is not
a directly supplied velocity measurement. The roughly 0.11 s lifetime comes
from their empirical relation, with substantial scatter and limitations for
hot, thin convection zones. These are comparisons, not exact calibration
values or a uniquely specified surface movie.

The model star's radius is 9,018 km. The adopted full-star composition samples
about 17 km per pixel near disk center. A physical granule is therefore about
0.05 pixel before the optical PSF and 1.79 s physical exposure. Its individual
morphology is unresolved. Mean effects already represented by the static
hydrogen spectrum and DA-3D broadband limb fits are retained. No new dynamic
3D spectral correction is claimed.

## What the local tests established

A reduced compressible grey RHD experiment was developed locally. It uses
ideal LTE H2/H/H+/electron chemistry, pure-H Ferguson/OPAL Rosseland means,
MUSCL/minmod reconstruction with Rusanov fluxes, SSPRK2 time integration,
constant gravity and conservative radiative heat exchange. Eight discrete
ordinates include horizontal radiative exchange. Periodic horizontal
boundaries surround a 3.2 km box, about 1.11 km deep; the lower gas boundary
reflects and the upper boundary transmits perturbations.

EOS consistency, positive heat capacity/sound speed, closed/open mass-energy
budgets and integrated radiative flux checks passed. A 16-cubed run completed
8 local seconds and reached mean late flux 1.00117 times the prescribed flux.
Those equation checks and thermal balance did not establish a correct
white-dwarf granulation field.

Its late vertical-intensity RMS was 2.37%, its locally sampled photospheric
RMS Mach was 0.13, and its logarithmic-power spectrum peaked at the box
fundamental, 3.2 km. The late sample did not show an e-folding decay within
its approximately 0.58 s correlation window. This is a failed comparison,
not a measured infinite lifetime. The Mach sampling differs from the
published horizontal mean-depth convention, so that numerical comparison
is an order-of-magnitude diagnostic, not an exact like-for-like measurement.

## Why the pattern is broad and persistent

The expected 0.85 km scale has only 4.3 horizontal grid cells in the coarse
run. Its photospheric pressure scale height has only about 1.35 vertical
cells. Hydrodynamic numerical dissipation and unresolved stratification are
credible causes of weak, large-scale flow. The stable pattern is dominated
by one box-scale wavelength, which is not a resolved granular ensemble.

The bilinear radiation stencil also damps short spatial wavelengths. The
analytically measured single-axis amplitude transfer at a 0.85 km wavelength
is about 0.768 per vertical-layer remapping on the coarse grid, versus 0.939
on the 32-cubed grid. These are stencil transfer factors, not measured
physical damping rates. They identify a numerical filtering mechanism; they
do not isolate a unique cause of the nonlinear flow failure.

The shallow bottom, ideal chemistry, grey opacity and limited angular
quadrature remain additional model uncertainties. Published DA calculations
use substantially better resolved, validated domains and microphysics.
Grey transfer alone is not proof of failure: Kupka et al. (2018) also used
grey transfer, with a deep, well-resolved model. A causal attribution among
these limitations would require controlled convergence and boundary tests.

## Why refinement stopped

The 16-to-32 conservative warm-start test fails after about 0.007 s in a
very dilute upper cell (density approximately 9e-13 g/cm^3). The fluid update
takes its temperature below the opacity table's 501 K lower limit. Halving
the hydrodynamic time step reaches the same unsupported range at nearly the
same elapsed time. At the failing increment the hydro-only temperature
matches the combined increment; the radiation-only temperature is unchanged
to reported precision, with opacity about 2.1e-9 cm^2/g.

This excludes a simple excessive radiative-cooling step as the direct trigger
of this particular failure. It does not prove the resulting cold state is
physical, nor diagnose a unique hydrodynamic/boundary defect. The table-domain
failure prevents a refinement convergence result. The code stops rather than
clamping temperature, extrapolating opacity or accepting an unchecked state.

Evidence: `convection-failure-diagnosis.json`,
`convection-resolution-audit.json`, `ordinates16-assessment.json`, and
`lte-equations.json` under `production/validation/`. Experimental flow
snapshots and solver development remain local and are not production inputs.

## Final decision

The local flow remains rejected. Matching the mean emergent flux alone is
insufficient. Enlarging, amplifying or re-timing its incorrect cells would
conceal the failure. The final renderer uses only the existing six-mode
pulsational temperature field, hybrid static atmospheric radiation, weak
Schwarzschild propagation and a normalized virtual optical model.

The fixed-observer light curve is reused unchanged from the validated physical
calculation. It is independent of the camera, false colors and display gain.
No conclusion about convective mode driving, nonlinear saturation or magnetic
spots is inferred from the failed granulation experiment.

References: [Tremblay et al. 2013b](https://arxiv.org/abs/1307.2810),
[Tremblay et al. 2013a](https://arxiv.org/abs/1302.2013),
[Kupka, Zaussinger & Montgomery 2018](https://doi.org/10.1093/mnras/stx3119).
