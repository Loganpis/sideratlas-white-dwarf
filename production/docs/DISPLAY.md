# Fixed surface display and optical imaging

The six mode temperatures, their amplitudes, frequencies, angular harmonics,
relative delays, atmospheric spectral radiance and fixed-observer photometry
remain unchanged. The display is a scientific diagnostic, not a telescope
image or the star's true visible color. No gas displacement is inferred from
the apparent movement of color boundaries.

The normalized optical calculation still redistributes physical radiance
through a circular-aperture diffraction core, Gaussian pointing jitter and
Moffat scattering wings. The halo retains the DA spectrum. Physical energy
checks occur before any false-color or contrast display transformation.

The enhanced map uses a fixed ±160 K pulsational temperature range and
u = asinh(deltaT / 12 K) / asinh(160 / 12). Its color anchors are specified
in config.json: deep blue through pale blue to near-white, with no per-frame
histogram or exposure adjustment. Warm/cool refers to a departure from
11290.02 K, not a mapping of optical wavelength into true surface colors.

A fixed diagnostic luminance gain exp(1.8*u*coverage) reveals pulsations without
altering the temperatures or source radiance. This enhancement is not
physical luminosity. The displayed core is therefore not suitable for
quantitative photometry. Fixed luminance tone mapping 1.2*Y/(1+1.2*Y), followed
by gamut compression toward neutral at constant luminance, replaces the
previous independent-channel exponential clipping.

Visible granulation is excluded after its local validation failure. No
spatial magnification, secondary flow clock or added flicker is used.

Scattered light is 4.5% of the same source light, not an additional emitting atmosphere. The optical
instrument is virtual: no aperture, source distance or measured telescope
image is claimed.

The only movie labels are THE WHITE DWARF, @sideratlas and NO.003. Slow camera
motion retains B's original inclination/azimuth scan. Physical observer
photometry remains at inclination 55 degrees, azimuth 0, independent of that
camera and all diagnostic color/contrast operations.
