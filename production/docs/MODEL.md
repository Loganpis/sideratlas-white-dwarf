# Model, imaging and limitations

## Equilibrium and oscillations

The supplied WDEC model has mass 0.593157405 solar masses, radius
9,018.133762 km, Teff 11,290.020041 K and log g = 7.9857501. Its
parameterized C/O core and H/He layers are reused from GYRE's supplied
equilibrium. No new progenitor evolution, diffusion history or MESA track
was calculated. GYRE 9.1.1 solves the linear adiabatic nonradial equations
with gravitational-potential perturbations included.

| l | radial g order | real angular m | local Newtonian period (s) |
|---|---|---|---|
| 1 | 4 | 0 | 315.7823650793 |
| 1 | 6 | 1 | 397.3374430687 |
| 1 | 8 | -1 | 488.1545239796 |
| 2 | 6 | 1 | 247.4518483943 |
| 2 | 8 | 2 | 286.9182814124 |
| 2 | 10 | -2 | 348.6856801177 |

Real harmonics describe standing angular patterns; these m labels do not
imply stellar rotation. High radial order is internal and is not drawn as
extra surface rings. Surface flux is

    f(n,t) = sum_j A_j H_lm(n) cos[2 pi (t - delay)/P_infinity,j + phase_j]
    Teff(n,t) = T0 [1 + f(n,t)]^(1/4)

The six selected modes have equal prescribed surface-flux variance, not
equal mode energy. The resulting linear, long-time/full-sphere temperature
RMS is 40.2343 K. The subset, m assignments, phases and amplitudes are not
predicted by the eigenproblem. No growth-rate-based mode selection,
nonlinear saturation, magnetic spots or dynamical convection filter is used.
The spherical emitting surface has no prescribed radial displacement,
rotational flow or pulsational Doppler velocity. Eigenfunctions and inertias
are retained as numerical results; their normalization is not a measurement
of the star's actual displacement amplitude.

## Atmosphere and weak gravitational propagation

Published Koester pure-H, hydrostatic LTE DA flux spectra are interpolated at
the local Teff and gravity. Claret DA-3D four-term broadband limb coefficients
are interpolated in atmospheric parameters and nominal band wavelengths.
The angular law L_lambda(mu) is normalized to preserve the spectral flux:

    I_lambda,em(mu) = F_lambda L_lambda(mu) / [2 pi integral_0^1 mu L_lambda(mu) dmu]

This remains a declared hybrid of 1D spectra and 3D broadband limb fits, not
a monochromatic 3D atmosphere or a matched time-dependent transfer solution.
Convective mean effects represented in those input models are retained;
individual granules are not resolved or synthesized. No new RHD data are
substituted for the saved atmosphere without a matching validated grid.

The direct Schwarzschild ray map supplies weak light bending and relative
propagation delays. With compactness u = 2GM/(Rc^2) = 0.000194203 and
g = sqrt(1-u),

    I_lambda,obs(lambda) = g^5 I_lambda,em(g lambda)
    P_infinity = P_GYRE / g
    z = 1/g - 1 = 0.0000971155

The equivalent redshift is 29.11 km/s, not an actual outflow. Applying a
constant surface clock factor to Newtonian modes is an approximation, not
relativistic asteroseismology. Such small corrections are below several
structural uncertainties and are never visually exaggerated.

CIE 1931 integration over 360–830 nm produces XYZ and linear sRGB. The
65-temperature × 129-sqrt(mu) radiation lookup table is the existing cache.
Production evaluation uses the identical bilinear interpolant, evaluating
only the four required RGB and Y channels. Its equivalence to the retained
general interpolator is checked numerically, rather than changing radiation
physics for speed.

## Camera, time and observer

One cosine-eased scan moves from inclination 55 to 70 degrees and azimuth
-25 to +25 degrees over 32 display seconds, with fixed -20-degree image
roll. It samples a sequence of distant static views, with no assigned
spacecraft trajectory or observer Doppler shift. The star stays centered at
(0.5, 0.565) in the portrait frame; its radius is 0.49 of the frame width.
The title is centered horizontally above the star.

The 32-second film spans 1,721.6 observer seconds at 53.8x speed. Each frame
uses two Gauss-Legendre shutter samples. Noncommensurate modes evolve
continuously; no phase forcing, repeated segment or forced seamless loop is
introduced. The camera is not stellar rotation.

The companion physical light curve uses a fixed observer at inclination
55 degrees and azimuth zero. It integrates physical CIE Y radiance,
spherical cancellation and per-ray delays over that fixed view at the same
shutter times. It does not sum false-color pixels or follow the movie camera.
Two antisymmetric real modes cancel at linear order for this observer while
remaining visible as local patterns from other directions.

## Optical image and false color

The virtual normalized imaging kernel is

    PSF = 0.955 (polychromatic Airy core * Gaussian jitter) + 0.045 Moffat wings

At 1080-pixel width the Airy first-zero radius is 3.8 pixels at 550 nm and
scales with wavelength. Gaussian jitter sigma is 0.6 pixel. The normalized
Moffat component has alpha = 40 pixels and beta = 2.5. These are explicit
instrument/display assumptions, not a measured telescope, assigned distance
or prediction of a stellar corona. 4.5 percent of the light is redistributed
into broad wings rather than added to the unchanged star.

The exact circular-aperture incoherent optical transfer function is averaged
over 65 wavelengths with the equilibrium DA spectrum and photopic response.
One effective core is used across the disk and color channels. Its departure
from full local wavelength-dependent imaging is an explicit approximation.
Tests against 1,881 wavelength nodes and varying local spectra check photopic
spectral quadrature and local-SED sensitivity; they do not quantify all omitted
RGB-specific diffraction fringes. Broad scattering is
achromatic and integrates the calculated spectral RGB. The halo's blue-white
chromaticity comes from the DA atmosphere, not an arbitrary glow color.

The fixed diagnostic scale is delta Teff = -160 to +160 K. Its mapping is

    u = asinh(deltaTeff/12 K) / asinh(160/12)
    v = (1 + u) / 2

A fixed deep-blue through blue-white palette is specified in config.json.
This is a temperature-departure diagnostic, not visible stellar color. No
per-frame histogram or exposure adjustment occurs. The asinh mapping enhances
small departures without changing the calculated temperature amplitudes.

The optically blurred temperature is intensity-weighted. Its palette is
normalized to CIE Y and mixed with physical spectral chromaticity at fixed
weight 0.96 inside the disk. Filtered geometric coverage fades the overlay
outside the star. An explicit diagnostic luminance gain exp(1.8*u*coverage)
makes the mode patterns more apparent. This gain is a visualization
transformation, not a change in stellar flux.

Fixed luminance tone mapping Y_display=1.2*Y_hdr/(1+1.2*Y_hdr), followed by
chroma compression toward neutral at constant displayed Y as needed, avoids
independent channel clipping. Displayed pixel brightness is not suitable for
physical photometry. The halo retains the calculated DA spectrum. The broad
wing fraction is reduced from 6% in v2.0.0 to 4.5%; normalized physical
linear radiance is checked before diagnostic color/gain/tone transforms.

Emission is integrated with 2x2 spatial samples, 8x8 samples at intersecting
limb pixels, analytic fractional circle coverage and a limiting inward ray
for tiny slivers. Imaging uses 384-pixel zero padding. Padded linear Y is
conserved within recorded numerical error; cropping legitimately loses a
small fraction outside the frame. Typography is composited after imaging.

## Accuracy and scope

The original 49-root search, integration refinements, radial eigenfunctions,
atmospheric spectral/angular checks and new optical validation are retained.
Selected numerical periods change by at most 6.84e-8 s under the final
integration refinement, but thinning the 435-point equilibrium to 218 points
shifts some periods by up to 1.017 s. This is a sensitivity test, not proof of
structural convergence. Frequency precision does not remove uncertainties
in composition, excitation, convection or atmosphere matching.

The movie is a calculated low-degree pulsation diagnostic with prescribed
excitation, physically modeled mean emission and a declared virtual imaging
system. It is neither a literal telescope image nor a self-consistent
three-dimensional hydrodynamic or magnetohydrodynamic stellar simulation.
