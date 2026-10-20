# Scientific data credits and terms

## CIE color-matching functions

Creator and rights holder: International Commission on Illumination (CIE)

Citation: CIE (2019), *Colour-matching functions of CIE 1931 standard
colorimetric observer*, CIE, Vienna, DOI
[10.25039/CIE.DS.xvudnb9b](https://doi.org/10.25039/CIE.DS.xvudnb9b)

[Official dataset landing page](https://cie.co.at/datatable/cie-1931-colour-matching-functions-2-degree-observer)

The original CSV and metadata, downloaded on 2026-10-17, are redistributed
**unmodified**:

- [Official CSV](https://files.cie.co.at/Publications-datasets/CIE_xyz_1931_2deg.csv)
- [Official metadata](https://files.cie.co.at/Publications-datasets/CIE_xyz_1931_2deg.csv_metadata.json)

CSV SHA-256: `fa663e3535a7e0763a745993a1f0a192eb0275ac46ad2d1befd7626841e713c1`

MD5: `17cca777db64b17170f06f67ce9d3ab7`

Both match the original metadata. The table has 471 rows over 360–830 nm,
with wavelength, x-bar, y-bar and z-bar columns. Original source: CIE
018:2019, Table 6.

The metadata identifies [Creative Commons Attribution-ShareAlike 4.0
International](https://creativecommons.org/licenses/by-sa/4.0/). Retain this
attribution, DOI, license link and modification status when sharing the
dataset. Adaptations of the dataset remain subject to those terms. These
data have their own license and are not relicensed under the repository's
software MIT license. CIE does not endorse this project.

The code interpolates the original matching functions and integrates
observer-frame spectral radiance to XYZ, scaled by 683 lm/W. The W3C
[color-conversion definitions](https://www.w3.org/TR/css-color-4/#color-conversion-code)
supply the standard XYZ/linear-sRGB matrix and sRGB transfer convention.
False-color diagnostics, the virtual PSF and the fixed display response are
separate declared visualization operations, described in MODEL.md.

## Atmosphere, interior inputs and fonts

Published Koester pure-H atmosphere spectra retain their authorship and SVO
service provenance. SVO distributes its Koester models with the author's
permission. The original Claret DA-3D table and ReadMe are retained. Exact
input URLs, parameters and SHA-256 values are in the `data/` provenance JSON
files. Their source attribution and terms remain distinct from the code license.

The supplied GYRE/WDEC equilibrium and controls are credited to their original
authors and GYRE's GPLv3 distribution. The GPL COPYING and WDEC license notices
are retained under `licenses/`, with the public source revision in SOURCES.md.
The compiled GYRE solver and MESA SDK are not redistributed. Calculated
eigenvalues and selected numerical results are supplied with their provenance.

The granulation assessment uses attributed numerical statistics from
Tremblay et al. (2013), not paper figures, a copied movie or a fabricated
simulation snapshot. Latin Modern fonts retain their bundled GUST/LPPL
notices. Citation and data availability do not imply third-party endorsement.
