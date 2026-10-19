J/A+A/641/A157      Limb-darkening coefficients for white dwarfs (Claret+, 2020)
================================================================================
Doppler beaming factors for white dwarfs, main sequence stars, and giant stars.
Limb-darkening coefficients for 3D (DA and DB) white dwarfs models.
    Claret A., Cukanovaite E., Burdge K., Tremblay P.-E., Parsons S., Marsh T.R.
    <Astron. Astrophys. 641, A157 (2020)>
    =2020A&A...641A.157C        (SIMBAD/NED BibCode)
================================================================================
ADC_Keywords: Models, atmosphere ; Photometry, SDSS ; Photometry, UBVRI
Keywords: white dwarfs - binaries: eclipsing - stars: atmospheres

Abstract:
    Systematic theoretical calculations of Doppler beaming factors are
    very scarce in the literature, mainly in the case of white dwarfs.
    Additionally, there are no specific calculations for the
    limb-darkening coefficients of 3D white dwarf models. The objective of
    this research is to provide the astronomical community with Doppler
    beaming calculations for a wide range of effective temperatures, local
    gravities and hydrogen/metal content for white dwarfs as well as stars
    on both the main sequence and the giant branch. In addition, for the
    first time we also present the theoretical calculations of the
    limb-darkening coefficients for 3D white dwarfs models. We computed
    Doppler beaming factors for DA, DB and DBA white dwarf models, as well
    as for main sequence and giant stars covering the transmission curves
    of the Sloan, UBVRI, HiPERCAM, Kepler, TESS, and Gaia photometric
    systems. The calculations of the limb-darkening coefficients for 3D
    models were carried out using the least-squares method for the same
    mentioned photometric systems. The input physics of the white dwarf
    models for which we have computed the Doppler beaming factors are:
    chemical compositions log[H/He]=-10.0 (DB), -2.0 (DBA) and He/H=0
    (DA), with logg varying between 5.0 and 9.5 and effective temperatures
    in the range 3750-100000K. The beaming factors were also calculated
    assuming non-local thermodynamic equilibrium (NLTE) for the case of DA
    white dwarfs with T_eff_>40000K. For the mixing-length parameters we
    adopted ML2/{alpha}=0.8 (DA case) and 1.25 (DB and DBA). The Doppler
    beaming factors for main sequence and giant stars were computed using
    the ATLAS9 version, characterized by metallicities ranging from [-2.5,
    0.2] solar abundances, with logg varying between 0 and 5.0 and
    effective temperatures between 3500-50000K. The adopted microturbulent
    velocity for these models was 2.0km/s. The limb-darkening coefficients
    were computed for 3D DA and DB white dwarf models calculated with the
    CO^5^BOLD radiation-hydrodynamics code. The parameter range covered by
    3D DA models spans logg values between 7.0 and 9.0, Teff between 6000
    and 15000K and He/H=0. The 3D DB models cover a similar parameter
    range of logg between 7.5 and 9.0, Teff between 12000 and 34000K and
    logH/He=-10.0. We adopted six laws for the computation of the
    limb-darkening coefficients: linear, quadratic, square root,
    logarithmic, power-2, and a general one with four coefficients. The
    beaming factor calculations which use realistic models of stellar
    atmospheres show that the black body approximation is not accurate,
    mainly for the filters u, u', U, g, g' and B. The black body approach
    is only valid for high effective temperatures and/or long effective
    wavelengths. Therefore, for more accurate analyses of light curves, we
    recommend the use of the beaming factors presented in this paper.
    Concerning limb-darkening, the distribution of specific intensities
    for 3D models indicates that in general these models are less bright
    towards the limb than their 1D counterparts, which implies steeper
    profiles. To describe these intensities better, we recommend the use
    of the four-terms law (also for 1D models) given the level of
    precision that is being achieved with Earth-based instruments, as well
    as space missions such as Kepler, TESS or PLATO in the future.

Description:
    Claret et al. (2020A&A...634A..93C, Cat. J/A+A/634/A93) derived LDCs
    for a set of one-dimensional DA, DB, and DBA white dwarf models. Here
    we compare these results to 3D model atmospheres for DA white dwarfs
    (DA-3D; Tremblay et al. 2013A&A...559A.104T) in the ranges
    logg=7.0-9.0 and Teff=6000-15000K, and for DB/DBA white dwarfs
    (DBA-3D; Cukanovaite 2018MNRAS.481.1522C, 2019MNRAS.490.1010C in the
    ranges logg=7.5-9.0 and Teff=12000-34000K.

File Summary:
--------------------------------------------------------------------------------
 FileName      Lrecl  Records  Explanations
--------------------------------------------------------------------------------
ReadMe            80        .  This file
tablebe.dat       46   108654  Doppler beaming for WD-DA, WD-DB, WD-DBA,
                                WD-DA-NLTE and ATLAS model,
                                Sloan (u'g'r'i'z'y'), UBVRI, HiPERCAM (ugriz)
                                and Kepler (Ke), TESS (Te), GAIA (Gbp, Gg, Grp)
tableu.dat        69     2436  u linear limb darkening coefficients,
                                Sloan (u'g'r'i'z'y'), UBVRI, HiPERCAM (ugriz)
                                and Kepler (Ke), TESS (Te), GAIA (Gbp, Gg, Grp)
tableab.dat       78     2436  a,b quadratic  darkening coefficients,
                                Sloan (u'g'r'i'z'y'), UBVRI, HiPERCAM (ugriz)
                                and Kepler (Ke), TESS (Te), GAIA (Gbp, Gg, Grp)
tablecd.dat       78     2436  c,d root-square limb darkening coefficients,
                                Sloan (u'g'r'i'z'y'), UBVRI, HiPERCAM (ugriz)
                                and Kepler (Ke), TESS (Te), GAIA (Gbp, Gg, Grp)
tableef.dat       78     2436  e,f logarithmic limb darkening coefficients,
                                Sloan (u'g'r'i'z'y'), UBVRI, HiPERCAM (ugriz)
                                and Kepler (Ke), TESS (Te), GAIA (Gbp, Gg, Grp)
tablegh.dat       78     2436  g,h power-2 limb darkening coefficients,
                                Sloan (u'g'r'i'z'y'), UBVRI, HiPERCAM (ugriz)
                                and Kepler (Ke), TESS (Te), GAIA (Gbp, Gg, Grp)
tablea4.dat       96     2436  a1,a2,a3,a4 limb darkening coefficients,
                                Sloan (u'g'r'i'z'y'), UBVRI, HiPERCAM (ugriz)
                                and Kepler (Ke), TESS (Te), GAIA (Gbp, Gg, Grp)
OriginalTab.tar 1128    18611  Original tables
--------------------------------------------------------------------------------

See also:
  J/A+AS/110/329 : LTE model atmospheres coeff. (Diaz-cordoves+, 1995)
  J/A+AS/114/247 : Limb-darkening coeff. for RIJHK (Claret+, 1995)
  J/A+A/335/647  : Limb-darkening coeff. for ubvyUBVRIJHK (Claret 1998)
  J/A+A/363/1081 : Non-linear limb-darkening law for LTE models (Claret, 2000)
  J/A+A/405/1095 : Limb-darkening coeff. from ATLAS9 models (Barban+, 2003)
  J/A+A/510/A21  : Stellar limb-darkening coeff. (Sing, 2010)
  J/A+A/529/A75  : Limb-darkening coefficients (Claret+, 2011)
  J/A+A/546/A14  : Limb-darkening for CoRoT, Kepler, Spitzer. I (Claret+, 2012)
  J/A+A/552/A16  : Limb-darkening for CoRoT, Kepler, Spitzer. II (Claret+, 2013)
  J/A+A/567/A3   : Limb-darkening coefficients for MOST (Claret+, 2014)
  J/A+A/600/A30  : Limb-darkening for TESS satellite (Claret, 2017)
  J/A+A/634/A93  : Limb-darkening coefficients for compact stars (Claret+, 2020)

Byte-by-byte Description of file (#): tablebe.dat
--------------------------------------------------------------------------------
   Bytes Format Units   Label     Explanations
--------------------------------------------------------------------------------
   1- 10  A10   ---     Model     Model (G1)
  12- 14  A3    ---     Filt      Filter (G2)
  15- 19  F5.2  [cm/s2] logg      Log10 Surface gravity
  21- 28  F8.1  K       Teff      Effective temperature
  30- 37  F8.4  ---     Z         Log10 [H/He]
  39- 46  F8.4  ---     Be        Doppler beaming for Fitler band
--------------------------------------------------------------------------------

Byte-by-byte Description of file (#): tableu.dat
--------------------------------------------------------------------------------
   Bytes Format Units         Label     Explanations
--------------------------------------------------------------------------------
   1- 10  A10   ---           Model     [WD-DA-3D WD-DB-3D] Model (G1)
  12- 14  A3    ---           Filt      Filter (G2)
  16- 20  F5.2  [cm/s2]       logg      Log10 Surface gravity
  22- 29  F8.1  K             Teff      Effective temperature
  31- 38  F8.4  ---           Z         Log10 [H/He]
  40- 47  F8.4  ---           u         Linear limb darkening coefficient u
  49- 56  F8.4  ---           sig       chi2 of linear LDC
  58- 69  E12.6 mW/m2/Hz/sr   I         Central intensity of linear LDC (G3)
--------------------------------------------------------------------------------

Byte-by-byte Description of file (#): tableab.dat
--------------------------------------------------------------------------------
   Bytes Format Units         Label     Explanations
--------------------------------------------------------------------------------
   1- 10  A10   ---           Model     [WD-DA-3D WD-DB-3D] Model (G1)
  12- 14  A3    ---           Filt      Filter (G2)
  16- 20  F5.2  [cm/s2]       logg      Log10 Surface gravity
  22- 29  F8.1  K             Teff      Effective temperature
  31- 38  F8.4  ---           Z         Log10 [H/He]
  40- 47  F8.4  ---           a         quadratic LDC coefficient a
  49- 56  F8.4  ---           b         quadratic LDC coefficient b
  58- 65  F8.4  ---           sig       chi2 of quadratic LDC
  67- 78  E12.6 mW/m2/Hz/sr   I         Central intensity of quadratic LDC (G3)
--------------------------------------------------------------------------------

Byte-by-byte Description of file (#): tablecd.dat
--------------------------------------------------------------------------------
   Bytes Format Units         Label   Explanations
--------------------------------------------------------------------------------
   1- 10  A10   ---           Model   [WD-DA-3D WD-DB-3D] Model (G1)
  12- 14  A3    ---           Filt    Filter (G2)
  16- 20  F5.2  [cm/s2]       logg    Log10 Surface gravity
  22- 29  F8.1  K             Teff    Effective temperature
  31- 38  F8.4  ---           Z       Log10 [H/He]
  40- 47  F8.4  ---           c       Root-square limb darkening coefficient c
  49- 56  F8.4  ---           d       Root-square limb darkening coefficient d
  58- 65  F8.4  ---           sig     chi2 for root-square LDC
  67- 78  E12.6 mW/m2/Hz/sr   I       Central intensity for root-square LDC (G3)
--------------------------------------------------------------------------------

Byte-by-byte Description of file (#): tableef.dat
--------------------------------------------------------------------------------
   Bytes Format Units         Label   Explanations
--------------------------------------------------------------------------------
   1- 10  A10   ---           Model   [WD-DA-3D WD-DB-3D] Model (G1)
  12- 14  A3    ---           Filt    Filter (G2)
  16- 20  F5.2  [cm/s2]       logg    Log10 Surface gravity
  22- 29  F8.1  K             Teff    Effective temperature
  31- 38  F8.4  ---           Z       Log10 [H/He]
  40- 47  F8.4  ---           e       Logarithmic limb darkening coefficient e
  49- 56  F8.4  ---           f       Logarithmic limb darkening coefficient f
  58- 65  F8.4  ---           sig     chi2 for logarithmic LDC
  67- 78  E12.6 mW/m2/Hz/sr   I       Central intensity for logarithmic LDC (G3)
--------------------------------------------------------------------------------

Byte-by-byte Description of file (#): tablegh.dat
--------------------------------------------------------------------------------
   Bytes Format Units         Label    Explanations
--------------------------------------------------------------------------------
   1- 10  A10   ---           Model    [WD-DA-3D WD-DB-3D] Model (G1)
  12- 14  A3    ---           Filt     Filter (G2)
  16- 20  F5.2  [cm/s2]       logg     Log10 Surface gravity
  22- 29  F8.1  K             Teff     Effective temperature
  31- 38  F8.4  ---           Z        Log10 [H/He]
  40- 47  F8.4  ---           g        Power-2 limb darkening coefficient g
  49- 56  F8.4  ---           h        Power-2 limb darkening coefficient h
  58- 65  F8.4  ---           sig      chi2 of exponential LDC
  67- 78  E12.6 mW/m2/Hz/sr   I        Central intensity of exponential LDC (G3)
--------------------------------------------------------------------------------

Byte-by-byte Description of file (#): tablea4.dat
--------------------------------------------------------------------------------
   Bytes Format Units         Label   Explanations
--------------------------------------------------------------------------------
   1- 10  A10   ---           Model   [WD-DA-3D WD-DB-3D] Model (G1)
  12- 14  A3    ---           Filt    Filter (G2)
  16- 20  F5.2  [cm/s2]       logg    Log10 Surface gravity
  22- 29  F8.1  K             Teff    Effective temperature
  31- 38  F8.4  ---           Z       Log10 [H/He]
  40- 47  F8.4  ---           a1      4terms limb darkening coefficient a1
  49- 56  F8.4  ---           a2      4terms limb darkening coefficient a2
  58- 65  F8.4  ---           a3      4terms limb darkening coefficient a3
  67- 74  F8.4  ---           a4      4terms limb darkening coefficient a4
  76- 83  F8.4  ---           sig     chi2 of 4terms LDC
  85- 96  E12.6 mW/m2/Hz/sr   I       Central intensity of 4terms LDC (G3)
--------------------------------------------------------------------------------

Global notes:
Note (G1): Models as follows:
   WD-DA-3D   = WD DA 3D models
   WD-DB-3D   = WD DB 3D models
   WD-DB      = WD DB models
   WD-DBA     = WD DBA models
   WD-DA      = WD DA models
   WD-DA-NLTE = WD DA-NLTE models
   ATLAS      = ATLAS model
Note (G2): Filters:
   Ke  = Kepler band
   Tes = Tess band
   Gb  = Gaia Gbp band
   G   = Gaia G band
   Gr  = Gaia Grb band
   u   = HiPERCAM u band
   g   = HiPERCAM g band
   r   = HiPERCAM r band
   i   = HiPERCAM i band
   z   = HiPERCAM z band
   u'  = SDSS u' band
   g'  = SDSS g' band
   r'  = SDSS r' band
   i'  = SDSS i' band
   z'  = SDSS z' band
   U   = U band
   B   = B band
   V   = V band
   R   = R band
   I   = I band
Note (G3): units are ergs/cm^2^/s/Hz/ster.
--------------------------------------------------------------------------------

Acknowledgements:
    Antonio Claret, claret(at)iaa.es

================================================================================
(End)                                        Patricia Vannier [CDS]  29-Jul-2020
