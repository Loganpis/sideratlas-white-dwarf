# Convection, granulation and magnetic spots

## Published radiation-hydrodynamic constraints

The scale assessment uses six neighboring pure-H CO5BOLD DA models from
Tremblay et al. (2013), Table 1, rather than a new hydrodynamic calculation.
The measured columns are characteristic granule size, bolometric vertical
intensity contrast, photospheric Mach number, pressure scale height and
density. Interpolation in Teff and log g gives a neighbor-model estimate;
it is not a new matched atmosphere solution. The selected rows and complete
calculation are in `validation/surface-physics.json`.

At 11,290 K and log g = 7.98575, the estimated scale is 0.85 km, the bolometric
intensity RMS is about 17%, and Mach is about 0.65. Inferring velocity from
`v_rms = Mach sqrt(Gamma1 g Hp)` gives roughly 7–9 km/s **conditional on**
Gamma1 between 1 and 5/3; the RHD table does not supply a matching Gamma1.
These estimates are not imposed gas motions. The intensity contrast is not
a local effective-temperature perturbation or a photopic contrast. Its
radiation-temperature proxy is not added to the pulsation model.

The adopted geometry has about 17 km per pixel near disk center. Thus the
characteristic cell spans about 0.05 pixel. The 550 nm diffraction core cuts
off spatial periods below roughly 53 km, before additional jitter, scattering
and exposure averaging. Individual granules are therefore unresolved. Low
spatial-frequency granulation noise need not vanish, but no raw RHD time
sequence or validated global stochastic model is available here to predict it.

**Decision:** preserve the existing mean atmosphere approximation and DA-3D
broadband limb fits; do not paint visible convective cells or invent global
flicker. The rejected local RHD experiment is documented in
[CONVECTION-AUDIT.md](CONVECTION-AUDIT.md). No calculated flow from that
experiment is included, and the whole atmosphere is not claimed to be
dynamically smooth. The displayed colors specifically
trace the low-degree pulsational Teff field.

## Convection response and mode driving

The earlier diagnostic converted the retained WDEC arrays to GSM 1.10 to
supply a zero background-cooling coefficient for GYRE's nonadiabatic equations.
It reproduced the retained adiabatic frequencies, but two frozen-convection
closures yielded surface flux-to-displacement responses differing by roughly
a factor of four. That numerical experiment does not validate convective
driving or the thermal response of this particular star.

The current movie uses none of those nonadiabatic responses, growth rates,
thermal phases or the earlier prescribed envelope filter. Physically motivated
convection is essential to ZZ Ceti driving; it cannot be replaced by an
unvalidated surface animation. The selected mode amplitudes and phases remain
explicit excitation assumptions, with a linear full-sphere/long-time
temperature RMS of 40.23 K. No nonlinear saturation prediction is claimed.

A short photospheric cell lifetime does not determine the heat-storage and
flux-response time of the deeper convection zone. In particular, the RHD
granulation clock is not a calibrated value of the envelope response time
used in pulsation theory. It is not used to assign new mode phases or driving.

## Magnetic compatibility

Tremblay et al. (2015) found that sufficiently strong fields suppress
photospheric convective transport. Gentile Fusillo et al. (2018) tested
convective and radiative atmosphere fits for a magnetic DA. Rui, Fuller &
Hermes (2025) show that fields can also shift frequencies and suppress g-mode
propagation. None supplies a spot solution for this particular model.

The conclusion is **not** that every field eliminates pulsations or that
magnetic spots can never coexist with a ZZ Ceti star. Rather, an imposed spot
map with unchanged nonmagnetic frequencies and atmosphere would lack a
calculated physical basis. It would require a specified field geometry,
magnetoconvective atmosphere and mode/thermal consistency checks. Weak fields
that barely affect convection do not automatically justify a visible dark spot.

**Decision:** retain the nonmagnetic equilibrium and modes. No spots, Zeeman
effects, magnetic mode shifts or magnetic surface transport are introduced.

References and original links are in [SOURCES.md](SOURCES.md). The decisions
above improve the physical scope assessment; they do not represent a new
resolved convection or MHD simulation.

## Local validation and release fallback

The local grey RHD test failed the scale, persistence and refinement checks.
The current release uses the user-authorized no-visible-granulation fallback.
The mean atmosphere approximation is retained without an invented dynamic
correction. See [CONVECTION-AUDIT.md](CONVECTION-AUDIT.md) for the bounded
failure diagnosis and numerical evidence.
