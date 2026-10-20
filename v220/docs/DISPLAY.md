# Fixed display and luminous imaging

Every changing large-scale structure follows the six preserved mode phases.
There is no artificial surface deformation or displacement of eigenfunctions.
Fine cellular changes follow the reproducible statistical model described in
CONVECTION.md. They are not extra GYRE modes or calculated fluid trajectories.

## Pulsation diagnostic

A fixed +/-160 K scale encodes the calculated mode temperature perturbation:

u = asinh(clamp(DeltaT,-160,160)/4) / asinh(160/4)

The palette is fixed blue to blue-white (all RGB anchors are in config.json).
The palette blend strength is 96%. It is false color, not the true visible color of a resolved white dwarf. The
physical temperature amplitudes, mode frequencies and phases are unmodified.
After filtering, a gain 2.7*u is added to log-luminance to reveal pulsation
interference. There is no frame-dependent histogram or automatic exposure.

## Optical calculation versus display enhancements

The physical spectral RGB field is filtered with a normalized polychromatic
circular-aperture Airy OTF (first zero at 550 nm =3.8 pixels at 1080 width),
Gaussian jitter sigma=0.6 pixels, and a broad Moffat beta=2.5 component with
alpha=85 pixels. Broad-scatter fraction is 0.12. Parameters scale with image
resolution. The prescribed virtual instrument is not any named telescope,
absolute angular resolution or physical distance.

Before applying display enhancements, padded linear CIE-Y flux conservation
is measured for the core/halo mixture. That check does not assert conservation
of the final diagnostic RGB image. Cropping, false colors, contrast, gain,
nonlinear tone mapping and display gamut compression change displayed flux.

A sixth source channel holds Y*G for the grey granular proxy. The core-filtered
ratio filtered(Y*G)/filtered(Y) modulates display log-luminance with exponent 4.
It is not an additional thermal spectrum or physical temperature amplitude.
The core display is 0.94*sigmoid(log[1.7*(1-0.12)*Ycore] + 2.7*u*coverage
+ 4*log(Gfiltered)*coverage). A fixed sixfold display gain makes the broad
halo more visible. Halo RGB comes from the calculated DA spectrum; the surface
false-color palette does not color the outer halo. The remaining luminance
headroom blends the mapped halo into the core without washing out the texture.
A fixed luminance-preserving gamut compression produces valid sRGB values.

The halo is an imaging/display effect, not a physical stellar atmosphere
extending hundreds of kilometers beyond the surface. The final image is a
scientific visualization, not an apparent telescope image or calibrated
photometric measurement. The caption discloses these choices outside the Reel.

## Sampling, motion and format

Native final frames are 1080x1920, with 2x2 source sampling, 8x8 limb sampling,
analytic pixel/circle coverage and two Gauss temporal samples. Cellular atlases
use 1025x2048 nodes and 0.005 local-second steps. The normalized mean field is
interpolated on the sphere with periodic longitude, not wrapped at the movie
boundary. B's slow camera is unchanged. Three labels use Latin Modern fonts.

The preview is eight seconds at 540x960/15fps, using the first eight seconds of
the same mode and camera schedule. The final film is one continuous 32-second,
30fps sequence with 960 distinct time samples. It is not a forced seamless
loop or four repetitions. H.264 High, 4:2:0, Rec.709 limited-range metadata,
explicit color conversion, high-quality compression and faststart are used.
