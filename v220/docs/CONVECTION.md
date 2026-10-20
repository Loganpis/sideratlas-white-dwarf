# Statistically constrained convection visualization

## What this is

A deterministic-seed, evolving cellular surrogate informed by DA radiation-
hydrodynamic literature. It is **not** a validated hydrodynamic flow, a recovered
CO5BOLD snapshot, a prediction of optical granulation, or output of the failed
local convection solver. No failed-flow outputs are imported or packaged.

Tremblay et al. (2013, A&A 557 A7), Table 1, provides neighboring DA models.
The interpolation retained in `validation/literature-constraints.json` suggests
a characteristic granulation length 0.8523 km and vertical bolometric intensity
RMS 17.2679%. Equation 16 gives an approximate intensity e-folding time 0.1105 s,
with intrinsic scatter and domain limitations. This is an empirical estimate,
not a directly measured lifetime for this exact star. The log(g)=8 rows at
11005 and 11529 K supply an interpolated bright-area fraction of 54.89%.
Neighbor interpolation is not a new matched RHD model.

These are bolometric intensity statistics. They do not uniquely imply local
Teff fluctuations, optical contrasts, emergent angle-dependent spectra, gas
velocities or convective fluxes. We do not make those identifications. Conditional
Mach-based velocity estimates in the retained audit are context only; the
surrogate does not solve or reproduce a fluid velocity field.

## Cellular construction

About 8192 finite-lived centers cover the sphere. A seeded stationary Poisson
birth process, lognormal lifetimes, smooth sin-squared growth/decay weights and
prescribed tangent drifts create continuously evolving spherical weighted
Voronoi cells. Two smallest weighted squared chord distances define an interior-
versus-boundary gap. A fixed analytic profile makes bright interiors and dark
lanes; no noise image, random per-frame texture or magnetic spot layer is added.
The solar granulation driver of Gudiksen & Nordlund (2005) is a geometric
precedent only. Its solar numerical scales are not used as DA constraints.

A profile power and offset are fitted to bright area and contrast. A dimensionless
time unit is fitted to the empirical e-fold time. Held-out directions and epochs
check contrast and decay. The fitted intensity field G is positive and normalized
to unit whole-sphere area mean at each atlas time. This removes global source
mean drift; it is not observer auto-exposure or a prediction of true granular
photometric variability. The finite birth catalog does not wrap periodically.

The held-out calibrated RMS is about 17.24%, bright fraction 54.90% and decay
0.1108 s. These are statistical calibration checks, **not validation of RHD**.
Spatial power peaks vary across finite patches; a median angular characteristic
wavelength 0.05210 rad defines the spatial mapping. At this star's radius it
corresponds to about 470 km: an explicit **551.3x magnification** of the 0.852 km
reference scale. Physical granules would be only 0.05 native pixels. The full-
star visual cell count is consequently much smaller than the physical count.

## Transfer, time and limitations

The existing calculated mode radiance is multiplied by G as a grey bolometric-
contrast proxy. There is no local cellular temperature calculation or new
atmosphere spectrum. The same mean limb law is used for all cells. Nonadiabatic
phase response, mode-dependent granulation statistics, fluid velocity, Doppler
signals and nonlinear mode/convection coupling are absent. Birth, drift,
lifetime distribution and morphology remain prescribed. Matching a few moments
does not establish the true spatial spectrum, probability distribution or
correlation function of a DA atmosphere.

The local convection display clock advances 0.05 s per displayed second; mode
physics advances 53.8 s. Light travel delays use each layer's own clock. Temporal
interpolation is at 0.005 local seconds on a 1025x2048 spherical atlas. Spatial
bilinear interpolation and the optical PSF smooth the narrowest boundaries;
`validation/cellular-numerics.json` quantifies this approximation. The intensity
contrast is additionally enhanced in display log-luminance by exponent 4, after
normalized optical filtering. It is not 4x the physical temperature fluctuation.

## Numerical display losses

Independent equal-area samples of the 1025x2048 atlas have about 16.63%
relative intensity RMS, versus 17.25% in the direct analytic cell field at the
same test time. Bilinear spatial interpolation smooths the narrowest lanes.
Halving the local time step changes intensity by 0.00089 RMS. In a native-pixel
image patch, after a one-pixel Gaussian proxy for core smoothing, the absolute
intensity RMS difference from direct evaluation is 0.00903. These are measured
numerical approximation errors, not proofs of hydrodynamic convergence.

The prescribed mean center lifetime is 3 dimensionless units, about 0.741 local
seconds after calibration. This is distinct from the approximately 0.11-second
intensity correlation decay: growing boundaries and changing cell dominance
can decorrelate intensity before a center disappears. Neither center lifetimes
nor tangent drift speeds are independently measured DA fluid quantities.
