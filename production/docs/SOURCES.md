# Primary references and input provenance

## Interior model and oscillations

- Bischoff-Kim & Montgomery (2018), *WDEC: A Code for Modeling White Dwarf Structure and Pulsations*, AJ 155, 187 — [DOI](https://doi.org/10.3847/1538-3881/aab70e)
- Townsend & Teitler (2013), *GYRE: an open-source stellar oscillation code based on a new Magnus Multiple Shooting scheme*, MNRAS 435, 3406 — [DOI](https://doi.org/10.1093/mnras/stt1533)
- Unmodified [GYRE 9.1.1](https://github.com/rhdtownsend/gyre/tree/v9.1.1), commit `d9ebbd1f3ca941042c5c9bd667102d9cf30c035b`; its supplied `models/wdec/m0.593/evolved` equilibrium and original WDEC controls are retained
- Wu & Goldreich (1999), *Gravity Modes in ZZ Ceti Stars. II. Eigenvalues and Eigenfunctions*, ApJ 519, 783 — [DOI](https://doi.org/10.1086/307412)
- Van Grootel et al. (2012), *The instability strip of ZZ Ceti white dwarfs. I. Introduction of time-dependent convection*, A&A 539, A87 — [DOI](https://doi.org/10.1051/0004-6361/201118371)
- [GYRE's documented convection closures](https://gyre.readthedocs.io/en/stable/ref-guide/osc-equations/conv-effects.html): used for a diagnostic sensitivity study, not as validated DAV convective driving

## Atmosphere and granulation

- Koester (2010), *White Dwarf Spectra and Atmosphere Models*, Mem. S.A.It. 81, 921 — [preprint](https://arxiv.org/abs/0812.0482)
- Published Koester pure-H flux spectra, distributed by the [SVO theoretical spectra service](https://svo2.cab.inta-csic.es/theory/newov2/index.php?models=koester2); exact files, URLs, parameters and hashes are in the retained `data/*spectra-provenance.json` files
- Tremblay & Bergeron (2009), hydrogen line profiles, ApJ 696, 1755 — [DOI](https://doi.org/10.1088/0004-637X/696/2/1755)
- Claret et al. (2020), DA-3D limb darkening, A&A 641, A157 — [DOI](https://doi.org/10.1051/0004-6361/202038436), [CDS tables](https://cdsarc.cds.unistra.fr/ftp/J/A+A/641/A157/); saved four-term coefficients supply the broadband angular approximation
- Tremblay et al. (2013a), *Pure-hydrogen 3D model atmospheres of cool white dwarfs*, A&A 552, A13 — [preprint](https://arxiv.org/abs/1302.2013), [DOI](https://doi.org/10.1051/0004-6361/201220813)
- Tremblay et al. (2013b), *Granulation properties of giants, dwarfs, and white dwarfs from the CIFIST 3D model atmosphere grid*, A&A 557, A7 — [preprint](https://arxiv.org/abs/1307.2810); Table 1 supplies the neighboring RHD statistics used in the resolution audit, not a synthesized surface texture
- Tremblay et al. (2013c), *Spectroscopic analysis of DA white dwarfs with 3D model atmospheres*, A&A 559, A104 — [preprint](https://arxiv.org/abs/1309.0886), [DOI](https://doi.org/10.1051/0004-6361/201322318); informs the distinction between full RHD, mean 3D structures and 1D spectra
- Hollands et al. (2026), *Any colour you like: the diverse chromaticities of white dwarfs* — [DOI](https://doi.org/10.1093/rasti/rzag069); investigated as a possible angle-resolved spectral improvement, but no matching private/request-only atmosphere grid is claimed or used

- Kupka, Zaussinger & Montgomery (2018), *Mixing and overshooting in surface convection zones of DA white dwarfs: first results from ANTARES*, MNRAS 474, 4660 — [DOI](https://doi.org/10.1093/mnras/stx3119); resolved grey-RHD context for the rejected local-flow audit

## Magnetic compatibility

- Tremblay et al. (2015), *On the Evolution of Magnetic White Dwarfs*, ApJ 812, 19 — [preprint](https://arxiv.org/abs/1509.05398), [DOI](https://doi.org/10.1088/0004-637X/812/1/19)
- Gentile Fusillo et al. (2018), *Can magnetic fields suppress convection in the atmosphere of cool white dwarfs? A case study on WD2105−820*, MNRAS 473, 3693 — [preprint](https://arxiv.org/abs/1710.02151), [DOI](https://doi.org/10.1093/mnras/stx2584)
- Rui, Fuller & Hermes (2025), *Supersensitive Seismic Magnetometry of White Dwarfs*, ApJ 981, 72 — [preprint](https://arxiv.org/abs/2410.20557)

These papers motivate excluding imposed magnetic spots from an unchanged
nonmagnetic mode calculation. They do not establish a universal prohibition
on magnetism and pulsation coexisting.

## Propagation, color and optics

- Pechenick, Ftaclas & Cohen (1983), *Hot spots on neutron stars: the near-field gravitational lens* — [DOI](https://doi.org/10.1086/161498); spherical direct-ray propagation context, used here in the very weak white-dwarf field
- [CIE 1931 2-degree color matching functions, official dataset](https://doi.org/10.25039/CIE.DS.xvudnb9b), CC BY-SA 4.0; retained unmodified with its metadata
- [W3C CSS Color 4 conversion definitions](https://www.w3.org/TR/css-color-4/#color-conversion-code), XYZ/linear-sRGB matrix and sRGB transfer conventions
- [Photutils circular-aperture Airy PSF](https://photutils.readthedocs.io/en/stable/api/photutils.psf.AiryDiskPSF.html)
- [Photutils normalized Moffat PSF](https://photutils.readthedocs.io/en/stable/api/photutils.psf.MoffatPSF.html)
- Trujillo et al. (2001), *The effects of seeing on Sersic profiles. II. The Moffat PSF* — [preprint](https://arxiv.org/abs/astro-ph/0109067)

The optics are an explicitly prescribed virtual instrument, not the PSF of
any named telescope. Latin Modern fonts retain the bundled GUST/LPPL notices.
Original source code is MIT; external data retain their individual credits
and terms. No NASA footage, generative texture, decorative turbulence or
invented magnetic map is used.
