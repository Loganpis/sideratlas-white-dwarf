# Physical foundation and scope — v2.2

This is a scientific visualization of a representative ZZ Ceti star. It is not
an observed star reconstruction, a telescope image, a new radiation-hydrodynamic
solution, or a nonlinear calculation of convection interacting with pulsations.

The preserved WDEC structure has M=0.5931574054 solar masses,
R=9018.13376175 km, Teff=11290.0200413 K and log(g)=7.985750095 (cgs).
The 435-point parametrized C/O-core structure and six GYRE 9.1.1 adiabatic
interior eigenvalues are unchanged. The modes include gravitational-potential
perturbations. Selected (ell,k,m) are (1,4,0), (1,6,1), (1,8,-1), (2,6,1),
(2,8,2), (2,10,-2). Their periods at infinity are approximately
315.813,397.376,488.202,247.476,286.946,348.720 seconds.

The model uses real standing spherical harmonics, not radial eigenfunction
nodes painted onto the surface. Surface flux amplitudes, m assignments,
phases, equal mode variance and the selected excitation scenario are prescribed.
Adiabatic GYRE does not predict the emergent temperature amplitudes, driving,
saturation or a validated convective transfer function.

F/F0 = 1 + sum_j A_j H_j(n) cos[2pi(t-delay)/P_j + phase_j]

Teff = T0 (F/F0)^(1/4)

The original temperature field has linear sphere/time RMS 40.234 K. Its physical
amplitudes and atmosphere cache are unchanged; only the display mapping is
stronger. A fixed +/-160 K color range is checked at every ray. No extrapolated
atmosphere temperatures, deformation, rotation, spots or flares are introduced.

## Radiation and gravity

Saved Koester pure-H 1D LTE spectra are integrated with CIE color matching
functions at 0.25 nm from 360 to 830 nm. Claret DA-3D broadband limb fits supply
an approximate angular law. This hybrid is not matched angle- and wavelength-
resolved 3D time-dependent transfer. The direct Schwarzschild ray map retains
weak bending, travel delays and spectral frequency shifts (g^5 for wavelength
specific intensity). Surface z=0.0000971155; GYRE local frequencies are redshifted
once. These small effects are not visually magnified.

## New cellular layer

See [CONVECTION.md](CONVECTION.md) for the independently calibrated statistical
surrogate. It modulates grey intensity, not calculated mode temperatures. It
is a separate visualization of convection statistics, with an explicitly
magnified spatial scale and a different display clock. Multiplication by the
mode radiance produces a coherent surface image but is not a calculated
physical interaction between convection and oscillations.

## Camera and time

The preserved B camera eases slowly from inclination 55 to 70 degrees and
azimuth -25 to +25 degrees; roll=-20 degrees. It does not represent stellar
rotation. The star remains centered on black, with only the three SiderAtlas
labels. The 32-second film spans 1721.6 seconds of the mode clock (53.8x faster).
The cellular clock advances 0.05 local seconds per display second (20x slower),
with local ray delay included. The two clocks deliberately reveal otherwise
incompatible timescales; this is not one simultaneous physical time sequence.

The copied fixed-observer light curve (inclination 55 deg, azimuth 0) contains
only the original physical mode radiation. It excludes camera motion, enlarged
cell flicker, false colors, tone mapping and halo gains. It must not be inferred
from the enhanced movie's total pixel brightness.

## Retained numerical evidence and limits

The original GYRE integration refinement changes the six local periods by at
most 6.84e-8 s between the fine and finer integrations on the same 435-point
background. The supplied WDEC regression test passed. Thinning the equilibrium
background to 218 points changes a selected period by as much as 1.0173 s.
That is a background sensitivity test, not a full stellar-structure convergence
proof or physical frequency uncertainty. The parametrized composition profile,
mode excitation and static atmosphere remain significant assumptions. The root
`validation/mode-convergence.json` retains the per-mode evidence; no newly
converged stellar equilibrium or nonadiabatic driving calculation is claimed.
