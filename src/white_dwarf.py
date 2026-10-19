"""Efficient radiative preview of prescribed, small-amplitude DAV surface modes.

No stellar interior eigenproblem, convection evolution or fluid velocity is
solved. Published DA spectra and DA-3D broadband limb laws supply the surface
emission. Schwarzschild redshift, direct-ray geometry and delays are computed.
"""
from dataclasses import dataclass,asdict
from pathlib import Path
import hashlib,json
import numpy as np
from numpy.polynomial.legendre import leggauss
from scipy.interpolate import RegularGridInterpolator

ROOT=Path(__file__).resolve().parents[1]
G=6.67430e-11
C=299792458.
MSUN=1.98847e30
RSUN=6.957e8
SIGMA=5.670374419e-8
LSUN=3.828e26


@dataclass(frozen=True)
class Star:
    mass_solar:float=.6
    temperature_k:float=12000.
    chand_mass_solar:float=1.44

    @property
    def radius_m(self):
        x=self.mass_solar/self.chand_mass_solar
        if not 0<x<1:raise ValueError('Cold mass-radius approximation requires 0<M<M_Ch')
        return .0112*RSUN*np.sqrt(x**(-2/3)-x**(2/3))
    @property
    def mass_kg(self):return self.mass_solar*MSUN
    @property
    def compactness(self):return 2*G*self.mass_kg/(self.radius_m*C**2)
    @property
    def redshift_factor(self):return np.sqrt(1-self.compactness)
    @property
    def logg_cgs(self):return np.log10(G*self.mass_kg/self.radius_m**2*100)
    @property
    def luminosity_w(self):return 4*np.pi*self.radius_m**2*SIGMA*self.temperature_k**4
    def parameters(self):
        return dict(**asdict(self),radius_km=self.radius_m/1000,
            earth_radii=self.radius_m/6371000,logg_cgs=self.logg_cgs,
            compactness=self.compactness,redshift_z=1/self.redshift_factor-1,
            redshift_equivalent_km_s=C/1000*(1/self.redshift_factor-1),
            temperature_at_infinity_k=self.temperature_k*self.redshift_factor,
            luminosity_solar=self.luminosity_w/LSUN,
            luminosity_at_infinity_solar=self.luminosity_w*self.redshift_factor**2/LSUN,
            surface_light_crossing_s=self.radius_m/C,
            apparent_radius_ratio=1/self.redshift_factor)


@dataclass(frozen=True)
class Mode:
    degree:int
    order:int
    period_infinity_s:float
    local_bolometric_semiamplitude:float
    phase_rad:float


# Representative clocks from G117-B15A; geometry, amplitudes and phases are
# prescribed for this generic star, not measured mode identifications or a fit.
MODES=(Mode(1,0,215.20,.030,.4),Mode(2,1,270.46,.012,1.2),Mode(1,1,304.05,.008,2.1))


def harmonic(degree,order,n):
    """Real spherical harmonics scaled to maximum absolute amplitude one.

    Condon–Shortley signs retained. These are normalized versions of
    Re(Y_l^m), not artificial surface textures. Only the selected low degrees
    are exposed to prevent silently using an unsupported normalization.
    """
    x,y,z=np.moveaxis(np.asarray(n),-1,0)
    if (degree,order)==(1,0):return z
    if (degree,order)==(1,1):return -x
    if (degree,order)==(1,-1):return -y
    if (degree,order)==(2,0):return .5*(3*z*z-1)
    if (degree,order)==(2,1):return -2*x*z
    if (degree,order)==(2,-1):return -2*y*z
    if (degree,order)==(2,2):return x*x-y*y
    if (degree,order)==(2,-2):return 2*x*y
    raise ValueError('Unsupported mode')


def flux_perturbation(normals,t_infinity,delay_s=0.,modes=MODES):
    value=0.
    for mode in modes:
        value=value+mode.local_bolometric_semiamplitude*harmonic(mode.degree,mode.order,normals)*np.cos(
            2*np.pi*(np.asarray(t_infinity)-delay_s)/mode.period_infinity_s+mode.phase_rad)
    return value


def temperature_from_flux(star,perturbation):
    if np.any(np.asarray(perturbation)<=-1):raise ValueError('Nonpositive local bolometric flux')
    return star.temperature_k*(1+np.asarray(perturbation))**.25


def ray_map(mu_em,compactness,quadrature=768):
    """Direct Schwarzschild rays: cos(psi), delay/(R/c), in the static frame.

    b/R=sqrt(1-mu_em²)/sqrt(1-u). Substitution x=R/r=1-s² removes
    the tangent-ray endpoint singularity. The delay is relative to the
    radial ray; a common propagation distance and Shapiro offset cancel.
    """
    mu=np.asarray(mu_em,float)
    if np.any((mu<0)|(mu>1)) or not 0<=compactness<.1:raise ValueError('Weakly compact star and outward rays required')
    nodes,weights=leggauss(quadrature);s=(nodes+1)/2;w=weights/2;x=1-s*s
    b2=(1-mu*mu)/(1-compactness)
    # Factored form of 1-b²x²(1-u*x), avoiding cancellation for tangent rays.
    f=mu[...,None]**2+b2[...,None]*s*s*(1+x-compactness*(1+x+x*x))
    if np.any(f<=0):raise ValueError('Invalid direct-ray radicand')
    root=np.sqrt(f)
    psi=np.sqrt(b2)*np.sum(2*s*w/root,axis=-1)
    delay=np.sum(2*s*w*b2[...,None]/(root*(1+root)),axis=-1)
    return np.cos(psi),delay


def limb_law(mu,coefficients):
    mu=np.asarray(mu,float)
    powers=mu[...,None]**(np.arange(1,5)/2)
    return 1-np.sum(np.asarray(coefficients)*(1-powers),axis=-1)


def limb_integral(coefficients):
    """Exact integral of I(mu)/I(1) times mu, over 0..1."""
    return .5-np.sum(np.asarray(coefficients)*(.5-1/(2+np.arange(1,5)/2)),axis=-1)


class DAAtmosphere:
    """Published 1D flux spectra + interpolated 3D broadband limb profiles.

    This is a declared hybrid: not a monochromatic 3D atmosphere solution.
    The broad passband limb laws are interpolated over optical wavelength;
    each monochromatic approximate profile is normalized to the DA flux.
    """
    bands=('U','B','V','R','I')
    band_centres_nm=np.array([365.,445.,551.,658.,806.])
    def __init__(self,data=ROOT/'data'):
        self.data=Path(data)
        self.provenance=json.loads((self.data/'spectra-provenance.json').read_text())
        self.spectra={}
        for record in self.provenance['records']:
            p=ROOT/record['file']
            if hashlib.sha256(p.read_bytes()).hexdigest()!=record['sha256']:raise ValueError('Modified atmosphere input')
            raw=np.loadtxt(p)
            if np.any(np.diff(raw[:,0])<=0) or np.any(raw[:,1]<=0):raise ValueError('Invalid atmosphere grid')
            # Angstrom -> nm; erg/cm²/s/Angstrom -> W/m²/nm.
            self.spectra[(record['teff_k'],record['logg_cgs'])]=(raw[:,0]*.1,raw[:,1]*.01)
        self.temperatures=np.array(sorted({k[0] for k in self.spectra}))
        self.gravities=np.array(sorted({k[1] for k in self.spectra}))
        self.ld={}
        for line in (self.data/'claret-2020-a4.dat').read_text().splitlines():
            values=line.split()
            if values and values[0]=='WD-DA-3D' and values[1] in self.bands:
                band=values[1];g=float(values[2]);t=float(values[3]);a=np.array(values[5:9],float)
                self.ld.setdefault((g,band),[]).append((t,a))
        self.ld_gravities=np.array(sorted({k[0] for k in self.ld}))
        cmf=np.loadtxt(self.data/'CIE_xyz_1931_2deg.csv',delimiter=',')
        self.cmf=cmf

    @staticmethod
    def bracket(grid,value):
        if not grid[0]<=value<=grid[-1]:raise ValueError('Atmosphere extrapolation forbidden')
        i=np.clip(np.searchsorted(grid,value,side='right')-1,0,len(grid)-2)
        f=(value-grid[i])/(grid[i+1]-grid[i])
        return int(i),float(f)

    def flux_spectrum(self,temperature,logg,wavelength_nm):
        i,f=self.bracket(self.temperatures,temperature);j,h=self.bracket(self.gravities,logg)
        result=0.
        for di,wt in ((0,1-f),(1,f)):
            for dj,wg in ((0,1-h),(1,h)):
                wave,flux=self.spectra[(self.temperatures[i+di],self.gravities[j+dj])]
                if np.min(wavelength_nm)<wave[0] or np.max(wavelength_nm)>wave[-1]:raise ValueError('Spectrum coverage required')
                result=result+wt*wg*np.interp(wavelength_nm,wave,flux)
        return result

    def coefficients(self,temperature,logg,wavelength_nm):
        j,f=self.bracket(self.ld_gravities,logg);bands=[]
        for band in self.bands:
            a=0.
            for dj,weight in ((0,1-f),(1,f)):
                rows=sorted(self.ld[(self.ld_gravities[j+dj],band)],key=lambda x:x[0])
                grid=np.array([v[0] for v in rows]);i,h=self.bracket(grid,temperature)
                a=a+weight*((1-h)*rows[i][1]+h*rows[i+1][1])
            bands.append(a)
        bands=np.array(bands)
        return np.stack([np.interp(wavelength_nm,self.band_centres_nm,bands[:,k]) for k in range(4)],axis=-1)

    def colour_radiance(self,temperature,logg,mu,redshift_factor=1.,step_nm=.25):
        """CIE XYZ and linear sRGB from observer-frame spectral radiance.

        Air wavelengths are used consistently for the published spectrum and
        color table. The minute redshift/air-dispersion cross term is omitted;
        this is broadband colorimetry, not precision wavelength metrology.
        """
        wave=np.linspace(360,830,round(470/step_nm)+1)
        emission_wave=redshift_factor*wave
        f=self.flux_spectrum(temperature,logg,emission_wave)
        a=self.coefficients(temperature,logg,emission_wave)
        integral=limb_integral(a)
        if np.any(integral<=0):raise ValueError('Nonpositive angular flux normalization')
        shape=limb_law(np.asarray(mu)[:,None],a[None,:,:])
        if np.any(shape<0):raise ValueError('Limb law predicts negative radiation')
        intensity=redshift_factor**5*shape*f[None,:]/(2*np.pi*integral[None,:])
        cmf=np.stack([np.interp(wave,self.cmf[:,0],self.cmf[:,k]) for k in (1,2,3)],axis=-1)
        xyz=683*np.trapz(intensity[...,None]*cmf[None,:,:],wave,axis=1)
        matrix=np.array([[3.24096994,-1.53738318,-.49861076],[-.96924364,1.8759675,.04155506],[.05563008,-.20397696,1.05697151]])
        return xyz@matrix.T,xyz


def build_colour_cache(star=Star(),output=ROOT/'data/colour-cache.npz'):
    atmosphere=DAAtmosphere();temps=np.linspace(11800,12200,41);mu=np.linspace(0,1,129)**2
    rgb=[];xyz=[]
    for temperature in temps:
        a,b=atmosphere.colour_radiance(temperature,star.logg_cgs,mu,star.redshift_factor)
        rgb.append(a);xyz.append(b)
    rgb=np.array(rgb);xyz=np.array(xyz)
    if np.any(rgb<=0):raise ValueError('Chosen DA colors fall outside positive sRGB cone')
    meta=dict(star=star.parameters(),temperature_nodes=temps.tolist(),mu_nodes=len(mu),
        spectral_sampling_nm=.25,spectrum='Koester pure-H LTE 1D DA spectra, SVO koester2',
        limb='Claret et al. 2020 DA-3D four-term UBVRI laws, interpolated in Teff/logg and nominal passband wavelength',
        approximation='Hybrid 1D flux + 3D broadband angular profiles; flux-conserving normalization, not a monochromatic 3D atmosphere',
        cmf='CIE 1931 2-degree observer, 360–830nm, no source-specific white balance',
        redshift='I_lambda,obs(lambda)=g^5 I_lambda,em(g*lambda)',
        input_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [ROOT/'data/claret-2020-a4.dat',ROOT/'data/CIE_xyz_1931_2deg.csv',Path(__file__)]})
    np.savez_compressed(output,temperature=temps,mu=mu,rgb=rgb,xyz=xyz,metadata=json.dumps(meta))
    output.with_suffix('.json').write_text(json.dumps(meta,indent=2)+'\n')
    return meta


class ColourCache:
    def __init__(self,path=ROOT/'data/colour-cache.npz'):
        with np.load(path) as data:
            self.temperatures=data['temperature'];self.mu=data['mu'];self.rgb=data['rgb'];self.xyz=data['xyz']
            self.metadata=json.loads(str(data['metadata']))
        self.interpolator=RegularGridInterpolator((self.temperatures,np.sqrt(self.mu)),np.concatenate((self.rgb,self.xyz),axis=-1),bounds_error=True)
    def intensity(self,temperature,mu):
        temperature,mu=np.broadcast_arrays(temperature,mu)
        return self.interpolator(np.stack((temperature,np.sqrt(mu)),axis=-1))


if __name__=='__main__':
    print(json.dumps(build_colour_cache(),indent=2))
