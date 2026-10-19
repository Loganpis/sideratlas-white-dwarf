from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import numpy as np
from numpy.polynomial.legendre import leggauss
from scipy.integrate import quad
from scipy.special import sph_harm
from white_dwarf import (Star,MODES,Mode,harmonic,flux_perturbation,temperature_from_flux,
    ray_map,limb_law,limb_integral,DAAtmosphere,ColourCache,SIGMA,C)


def test_representative_star_and_small_gravity_effects():
    star=Star();p=star.parameters()
    assert 8500<p['radius_km']<8800
    assert 8.0<p['logg_cgs']<8.05
    assert 30<p['redshift_equivalent_km_s']<32
    assert .00010<p['redshift_z']<.00011
    assert 11998<p['temperature_at_infinity_k']<12000
    assert .0028<p['luminosity_solar']<.0030
    assert p['apparent_radius_ratio']-1<.00011


def test_ray_integrals_recover_flat_space_angle_and_delay():
    mu=np.r_[0.,np.geomspace(1e-4,1,80)]
    cospsi,delay=ray_map(mu,0.)
    np.testing.assert_allclose(cospsi,mu,atol=2e-9)
    np.testing.assert_allclose(delay,1-mu,atol=2e-9)


def test_schwarzschild_weak_deflection_is_small_and_behind_limb():
    star=Star();mu=np.linspace(0,1,101)
    cospsi,delay=ray_map(mu,star.compactness)
    assert cospsi[0]<0
    assert np.max(abs(cospsi-mu))<.00021
    assert np.all(np.diff(cospsi)>0)
    assert np.all(np.diff(delay)<0)
    np.testing.assert_allclose(cospsi[-1],1.,atol=1e-14)
    np.testing.assert_allclose(delay[-1],0.,atol=1e-14)


def test_ray_integrals_agree_with_independent_adaptive_quadrature():
    u=Star().compactness
    mu=np.array([0.,.0001,.02,.3,.8,1.])
    cospsi,delay=ray_map(mu,u)
    for i,m in enumerate(mu):
        b2=(1-m*m)/(1-u)
        def root(s):
            x=1-s*s
            return np.sqrt(m*m+b2*s*s*(1+x-u*(1+x+x*x)))
        angle=quad(lambda s:2*s*np.sqrt(b2)/root(s),0,1,epsabs=1e-11,epsrel=1e-11)[0]
        dt=quad(lambda s:2*s*b2/(root(s)*(1+root(s))),0,1,epsabs=1e-11,epsrel=1e-11)[0]
        np.testing.assert_allclose(cospsi[i],np.cos(angle),atol=1e-10)
        np.testing.assert_allclose(delay[i],dt,atol=1e-10)


def test_selected_patterns_are_real_spherical_harmonics():
    rng=np.random.default_rng(30)
    n=rng.normal(size=(1000,3));n/=np.linalg.norm(n,axis=-1)[:,None]
    theta=np.arccos(n[:,2]);phi=np.arctan2(n[:,1],n[:,0])
    for mode in MODES:
        y=sph_harm(mode.order,mode.degree,phi,theta).real
        h=harmonic(mode.degree,mode.order,n)
        factor=np.dot(h,y)/np.dot(y,y)
        np.testing.assert_allclose(h,factor*y,atol=3e-14)
        assert np.max(abs(h))<=1


def test_nonradial_flux_has_no_artificial_global_monopole():
    mu,w=leggauss(32);phi=np.arange(64)*2*np.pi/64
    x=np.sqrt(1-mu[:,None]**2)*np.cos(phi)
    y=np.sqrt(1-mu[:,None]**2)*np.sin(phi)
    n=np.stack((x,y,np.broadcast_to(mu[:,None],x.shape)),axis=-1)
    for t in [0,73,215,400]:
        delta=flux_perturbation(n,t)
        assert abs(np.sum(delta*w[:,None])*(2*np.pi/64))<1e-14
        assert np.max(abs(delta))<=sum(m.local_bolometric_semiamplitude for m in MODES)
        temp=temperature_from_flux(Star(),delta)
        np.testing.assert_allclose((temp/12000)**4,1+delta,atol=1e-14)


def test_each_mode_uses_its_observer_period_and_photon_delay():
    n=np.array([[0.,0.,1.],[1.,0.,0.]])
    for mode in MODES:
        for delay in [0,.029]:
            a=flux_perturbation(n,27,delay,(mode,))
            b=flux_perturbation(n,27+mode.period_infinity_s,delay,(mode,))
            np.testing.assert_allclose(a,b,atol=1e-16)
            shifted=flux_perturbation(n,27-delay,0,(mode,))
            np.testing.assert_allclose(a,shifted,atol=1e-16)


def test_published_spectral_flux_scale_and_balmer_absorption():
    atmosphere=DAAtmosphere();star=Star()
    wave,flux=atmosphere.spectra[(12000.,8.)]
    fraction=np.trapz(flux,wave)/(SIGMA*12000**4)
    assert .99<fraction<1.01  # small UV/IR tails lie outside the downloaded range
    f=atmosphere.flux_spectrum(12000,star.logg_cgs,np.array([480.,486.1,492.]))
    assert f[1]<.8*(f[0]+f[2])/2


def test_limb_profiles_conserve_each_wavelength_flux():
    atmosphere=DAAtmosphere();star=Star()
    for temperature in [11850,12000,12150]:
        a=atmosphere.coefficients(temperature,star.logg_cgs,np.array([365.,445.,551.,658.,806.]))
        for row in a:
            integrated=quad(lambda mu:float(limb_law(mu,row))*mu,0,1,epsabs=1e-11)[0]
            np.testing.assert_allclose(integrated,limb_integral(row),rtol=1e-10)
            assert limb_law(0.,row)>0
            np.testing.assert_allclose(limb_law(1.,row),1.)


def test_colour_cache_and_spectral_sampling_errors_are_small():
    atmosphere=DAAtmosphere();star=Star();cache=ColourCache()
    mu=np.array([0.,.0003,.013,.2,.53,.99,1.])
    for temperature in [11923.,12000.,12067.]:
        direct,xyz=atmosphere.colour_radiance(temperature,star.logg_cgs,mu,star.redshift_factor)
        saved=cache.intensity(temperature,mu)
        np.testing.assert_allclose(saved[:,:3],direct,rtol=.0006)
        coarse,_=atmosphere.colour_radiance(temperature,star.logg_cgs,mu,star.redshift_factor,step_nm=.5)
        np.testing.assert_allclose(coarse,direct,rtol=.001)
        assert np.all(direct>0)
