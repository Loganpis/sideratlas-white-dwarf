# Physical model, final rendering and limits

## Scope and preserved foundation

The final film uses the original numerical model in `src/white_dwarf.py` **without changing its source, stellar parameters, modes, atmosphere spectra or radiation cache**. It is a generic, representative ZZ Ceti / pulsating hydrogen-atmosphere (DA) white dwarf. The visible changes are prescribed small-amplitude photospheric flux modes. Their emitted spectrum, angular radiation and propagation are then calculated. No expensive stellar-evolution, hydrodynamic, MHD or time-dependent convection calculation was added.

This is not a solved g-mode eigenvalue problem, nonadiabatic pulsation solution or fit to a particular observed star. Citing observed periods does not establish that these are the eigenfrequencies or mode identifications of the chosen 0.6 M☉ model. This distinction is retained in the caption.

## Equilibrium star

M = 0.6 M☉ and T₀ = 12,000 K are representative choices. With μₑ ≈ 2 and M_Ch = 1.44 M☉, the Nauenberg-style cold relation is

R = 0.0112 R☉ [(M_Ch/M)^(2/3) − (M/M_Ch)^(2/3)]^(1/2)

This gives R = 8,658.07 km ≈ 1.36 Earth radii, Newtonian log g = 8.02623 (cgs), and L = 4πR²σT₀⁴ ≈ 0.002893 L☉. Finite-temperature structure, detailed composition and hydrogen-envelope corrections to the radius are not solved. No distance, extinction, telescope or detector is assigned.

## Photospheric flux modes

At a unit surface normal n = (x,y,z) in the fixed mode frame,

δ(n,t) = Σ Aⱼ Hⱼ(n) cos(2πt/Pⱼ + φⱼ)

F_bol(n,t) = σT₀⁴ [1 + δ(n,t)]

T_eff(n,t) = T₀ [1 + δ(n,t)]^(1/4)

The real spherical harmonics are normalized to max|H| = 1, rather than unit integral of H²:

| ℓ,m | H | Observer-coordinate P | Local bolometric semi-amplitude | Phase |
| --- | --- | --- | --- | --- |
| 1,0 | z | 215.20 s | 0.030 | 0.4 rad |
| 2,1 | −2xz | 270.46 s | 0.012 | 1.2 rad |
| 1,1 | −x | 304.05 s | 0.008 | 2.1 rad |

These periods are observed examples reported for G117-B15A. The mode assignments, local amplitudes and phases are selected for this generic star, not its measured seismic solution. Local bolometric amplitudes are not observed disk-integrated photometric amplitudes. Each harmonic has zero full-sphere integral, so the prescribed simultaneous bolometric flux has no artificial luminosity monopole. Globally |δ| ≤ 0.05, giving temperature departures within approximately −153 to +147 K. No physical amplitude gain is applied.

Modes are standing patterns in a zero-rotation approximation. The superposition produces real mathematical interference: when the dominant dipole coefficient passes through zero near 255.30 s, the existing quadrupole supplies about 78.8% of instantaneous full-sphere flux-perturbation variance. Its lobes can then become more apparent. Only ℓ ≤ 2 structure exists: no higher-degree modes, spots, granular texture, spirals or other activity are inserted.

The geometry stays spherical. Displacement eigenfunctions, fluid velocities, rotational splitting, pulsational gravity variations, Doppler shifts, convective driving, nonlinear mode coupling and time-dependent atmosphere/convection response are not calculated. The quasi-static atmosphere responds to the prescribed local effective temperature, rather than to a solved fluid oscillation.

## Spectral and angular radiation

The original Koester pure-H, LTE, hydrostatic plane-parallel DA spectra are obtained via SVO on a 5-temperature × 2-gravity grid: T = 11,500–12,500 K and log g = 8.0, 8.25. The service supplies air wavelengths and emergent flux Fλ = 4π times Eddington flux. It is not treated as intensity. Unit conversion is 1 erg cm⁻² s⁻¹ Å⁻¹ = 0.01 W m⁻² nm⁻¹. Bilinear interpolation in T and log g retains the published Balmer absorption spectrum. The available wavelength range contains approximately 99.6% of σT⁴ at 12,000 K; the tiny omitted UV/IR tails are not invented or renormalized.

Claret et al. (2020) DA-3D four-term broadband limb profiles give

Dλ(μ) = 1 − Σₖ₌₁⁴ aₖ,λ [1 − μ^(k/2)]

Jλ = ∫₀¹ μDλ(μ) dμ

Iλ,em(μ) = Fλ Dλ(μ) / (2πJλ)

Thus 2π∫Iλ μdμ = Fλ exactly for the approximate angular law. Coefficients are interpolated in temperature, log g and nominal UBVRI wavelengths 365,445,551,658,806 nm, with endpoint clamping over the short intervals needed for the 360–830 nm color integration.

**Hybrid atmosphere limitation:** 1D spectral fluxes are combined with 3D broadband limb fits, rather than a self-consistent monochromatic 3D intensity solution. Passband interpolation does not resolve angular changes within individual Balmer lines, and an instantaneous local atmosphere is not a nonadiabatic response calculation. These assumptions are preserved from the approved model.

The official CIE 1931 2° functions are integrated at 0.25 nm spacing over 360–830 nm. A small existing cache stores physical RGB and XYZ radiance versus T and √μ. The final renderer evaluates only its CIE Y component with algebraically identical bilinear interpolation, verified against the original full-channel interpolator. There is no atmosphere extrapolation or source-dependent white balance.

## Weak-field photon propagation

The exterior is static Schwarzschild. With u = 2GM/(Rc²), g_r = √(1−u), and B = b/R = √(1−μ²)/g_r:

λ_obs = λ_em / g_r

Iλ,obs(λ_obs) = g_r⁵ Iλ,em(g_r λ_obs)

Bolometric intensity scales as g_r⁴. Apparent radius is R/g_r; total luminosity at infinity is g_r²L. Periods are already observer-coordinate clocks, so there is no second period redshift: the corresponding surface proper period is g_rP.

Direct outgoing rays use x = R/r and f = 1 − B²x²(1−ux):

ψ = B ∫₀¹ dx / √f

Δt/(R/c) = ∫₀¹ B² dx / [√f(1+√f)]

The latter subtracts radial travel time analytically, cancelling a common infinite-distance term. Substitution x = 1−s² regularizes the tangent endpoint; a factored radicand avoids cancellation. The original 768-point quadrature supplies a 4,097-node μ lookup. An independent adaptive reference with logarithmic subdivisions resolves the boundary layer of extremely grazing rays and validates the production lookup.

Each visible sample evaluates the original modes at t_obs−Δt. For this star u ≈ 0.000204665, z ≈ 0.000102348 (equivalent to 30.68 km/s), R/c ≈ 0.02888 s, and apparent-radius inflation ≈0.0102%. Redshift changes the color-temperature scale by only ≈1.23 K. These small effects are calculated without visually exaggerating them; no halo or photon ring is added.

The atmosphere still uses Newtonian log g. Its tiny relativistic correction, the air-wavelength/redshift dispersion cross term, extinction and observer velocities are omitted. This is broadband surface visualization, not precision radial-velocity spectroscopy.

## Fixed false-color temperature display

The approved B palette and contrast are retained:

s = asinh(ΔT / 18 K) / asinh(160 / 18)

palette = RdBu_r[(1+s)/2], with a fixed −160 to +160 K scale

ΔT is the shutter-mean local temperature departure from 12,000 K. Blue and red do not represent the star's emitted visible colors. There is no per-frame normalization. The near-zero color-coordinate slope is about 3.085 times that of a linear ±160 K map; this is a **display contrast enhancement**, not a physical temperature or radiation gain. The continuous segmented palette is evaluated at 4,097 distinct nodes to avoid a 256-color lookup creating false bands.

Compared with the short B preview, the final film improves atmospheric shading by using its small **time-dependent physical CIE Y radiance**, rather than only the equilibrium limb profile:

RGB_linear = 0.94 × linear_sRGB(palette) × ⟨I_Y,physical(T, μ)⟩_shutter / I_Y,equilibrium(center)

This preserves wavelength-integrated atmospheric brightness response and limb darkening. However, the palette itself changes luminance: **summing the false-color frame is not physical photometry**. The companion curve therefore uses the original physical intensity directly. No external illumination, grain, arbitrary surface texture, glow, contour or deformation is used. The only text is THE WHITE DWARF, @sideratlas and NO.003.

## Cinematic camera and fixed observer are different roles

The film's camera smoothly changes inclination 55→70° and azimuth −25→+25° over 32 seconds, with fixed roll −20°. Both angles use ease f(p) = [1−cos(πp)]/2. Surface-to-observer direction in mode coordinates is

n_obs = (−sin i cos az, −sin i sin az, cos i)

This is a sequence of distant static projection directions at constant unspecified distance, not a calculated material orbit. No camera velocity, Doppler effect, aberration, stellar spin or distance-dependent dilution is introduced. The same Schwarzschild map is reused by spherical symmetry. Projection is evaluated at each shutter sample; the angularly resolved scale and framing are presentation choices, not an assigned apparent size at a known distance.

**The companion light curve instead holds i = 55°, az = 0° fixed in the mode frame for the entire simulation.** It integrates the physical DA CIE Y radiation over that observer's projected disk, including the same retarded-time convention. It is completely independent of cinematic camera motion. It is not expected to equal the brightness of the film's changing hemisphere or false-color palette. The fixed observer is stated explicitly in the caption, metadata, CSV and separate scientific guide.

The fixed light curve uses 96 radial × 192 azimuthal quadrature nodes, independently checked with 144 × 288 and higher temporal order. Its normalization is the equilibrium disk at the same fixed direction. It is a CIE Y visible-flux curve, not bolometric luminosity or data measured from a particular white dwarf.

## Time, sampling, output and reproducibility

The final 32 seconds cover 1,721.6 observer seconds at 53.8× playback, preserving the short preview's mode speed while slowing the camera scan. There are eight dominant 215.20 s cycles; the other periods remain unrounded. The simulation is continuous, not four repeated clips or a forced seamless loop.

Rendering uses 1080 × 1920 at 30 fps (960 frames), 2×2 spatial samples per interior pixel, and 8×8 radiance samples near the limb. Analytic circle–rectangle overlap supplies exact fractional limb coverage, avoiding a stair-stepped 8×8 geometric edge. For extremely thin slivers containing no radiance subnode, an interior sliver point supplies intensity while retaining analytic area. This is a subpixel quadrature approximation; it creates no physical feature. No star-size or surface-shape oscillation is inserted.

Two-point Gauss–Legendre integration averages temperature and physical radiance across each frame shutter. The camera is evaluated at the same temporal nodes. Tests against four temporal nodes, 4×4 interior / 16×16 limb spatial sampling, denser disk integration, direct atmospheric interpolation and independent ray integration quantify numerical error in `validation/numerical-convergence.json`. The most localized spatial differences are confined to the steep limb profile; RMS and maximum errors are both reported rather than claiming exact convergence everywhere.

Spatial averaging and title composition occur in linear light. Frames remain 16-bit-per-channel sRGB until zscale converts them to Rec.709 limited-range YCbCr. Error diffusion at final 8-bit quantization reduces banding; it is an encoding operation, not astrophysical surface noise. H.264 High uses CRF 14 with a 20 Mb/s VBV cap, progressive yuv420p, a closed 2-second GOP and fast-start MP4. There is no audio. Platform delivery compression remains outside this calculation.

Four-second encoding checkpoints are concatenated without re-encoding. All 960 final presentation timestamps, including joins, are verified against n/30 seconds. Color-managed source-versus-decoded comparisons use the retained full-depth frame samples. The fixed-observer curve is checked independently at selected frames. Tests also cover coordinate rotations, analytic harmonic visibility factors, optimized retarded phases, cache interpolation, approved labels, black background and exact circular coverage. These checks establish implementation accuracy within the stated model; they do not validate prescribed amplitudes or a stellar interior against observations.
