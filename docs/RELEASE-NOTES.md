# v1.0.0 — SiderAtlas NO.003: THE WHITE DWARF

The approved slow camera scan is now a continuous, minimalist 32-second Reel. Only THE WHITE DWARF, @sideratlas and NO.003 remain on the black-background film. Technical overlays are confined to the scientific guide, caption and reproducibility files.

The original stellar source, mode parameters and atmosphere cache are preserved. The final rendering adds time-dependent atmospheric radiance shading, higher spatial and temporal sampling, analytic limb coverage, a high-depth input path and color-managed export. Temperature amplitudes are unchanged. Colors use the explicitly disclosed fixed ±160 K asinh false-color mapping.

The companion CIE Y light curve is computed for a fixed observer at i = 55°, az = 0°, independent of camera movement. The final 32 seconds cover 1,721.6 physical seconds at 53.8× speed; the camera makes one slower scan. The source is not repeated or forced into a seamless loop.

The release includes the movie, Instagram caption and a complete source/data/validation bundle. The bundle also contains retained full-depth frame samples, so its color-managed video checks can be run without first re-rendering the film. See `validation/final-validation.json` for measured export and photometry results, and `validation/numerical-convergence.json` for sampling and ray-lookup convergence. Check published downloads with `SHA256SUMS.txt`.

Scientific limits remain explicit: prescribed photospheric flux modes rather than a solved stellar-interior eigenmode spectrum, a cold radius estimate, hybrid 1D spectral fluxes / 3D broadband limb fits, a static spherical surface, and no solved convection, fluid motion or stellar rotation. This is a generic ZZ Ceti visualization, not a named-star reconstruction or a telescope image.
