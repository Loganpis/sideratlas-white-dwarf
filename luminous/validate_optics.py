"""Independent optical normalization, diffraction and spectral-averaging checks."""
from pathlib import Path
import sys,json
import numpy as np
from scipy.fft import rfftfreq,fftfreq,irfft2
from scipy.special import j0,j1
ROOT=Path(__file__).resolve().parent;BASE=ROOT.parent
sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(BASE/'src'))
from luminous_render import airy_otf,Optics,YROW
from mode_model import InteriorModes,ResearchAtmosphere
from white_dwarf import limb_law,limb_integral,ColourCache


def spectrum_mtf(config,nodes,temperature=None,mu=None):
    model=InteriorModes();s=model.star;a=ResearchAtmosphere();wave=np.linspace(360,830,nodes)
    flux=a.flux_spectrum(s.temperature_k if temperature is None else temperature,s.logg_cgs,wave*s.redshift_factor)
    if mu is not None:
        coeff=a.coefficients(s.temperature_k if temperature is None else temperature,s.logg_cgs,wave*s.redshift_factor)
        flux*=limb_law(np.full(len(wave),mu),coeff)/(2*np.pi*limb_integral(coeff))
    y=np.interp(wave,a.cmf[:,0],a.cmf[:,2]);weight=flux*y;weight[[0,-1]]*=.5;weight/=weight.sum()
    freq=np.linspace(0,.71,2049);out=np.zeros_like(freq)
    for lam,wt in zip(wave,weight):out+=wt*airy_otf(freq,config['airy_first_zero_px_at_550nm_1080']*lam/550)
    out*=np.exp(-2*np.pi**2*config['jitter_sigma_px_at_1080']**2*freq**2)
    return out


def main():
    cfg=json.loads((ROOT/'config.json').read_text());n=768
    f=np.hypot(fftfreq(n)[:,None],rfftfreq(n)[None,:])
    airy=irfft2(airy_otf(f,12),s=(n,n))
    axis=np.minimum(np.arange(n),n-np.arange(n));rad=np.hypot(axis[:,None],axis[None,:])
    ee=float(airy[rad<=12].sum())
    expected=1-j0(3.8317059702075125)**2-j1(3.8317059702075125)**2
    q=2*np.pi*10*f;moffat=irfft2((1+q)*np.exp(-q),s=(n,n))
    mee=float(moffat[rad<=30].sum());mexpected=1-(1+3**2)**-1.5
    reference=spectrum_mtf(cfg,1881);used=spectrum_mtf(cfg,65)
    spectral_error=float(np.max(abs(used-reference)))
    local=[];t0=InteriorModes().star.temperature_k
    for t in [t0-140,t0,t0+140]:
        for mu in [.02,.5,1.]:
            local.append(dict(temperature_K=t,mu=mu,max_absolute_MTF_difference=float(np.max(abs(spectrum_mtf(cfg,1881,t,mu)-reference)))))
    # A separate small numerical scene, with a well sampled PSF at this grid.
    test=dict(cfg)
    for k in ['airy_first_zero_px_at_550nm_1080','jitter_sigma_px_at_1080','moffat_alpha_px_at_1080']:
        test[k]*=1080/128
    optics=Optics((128,128),test,padding=128)
    cache=ColourCache(BASE/'data/research-colour-cache.npz');s=InteriorModes().star
    point=cache.intensity(s.temperature_k,np.array([1.]))[0];rgb=point[:3]/point[4]
    yy,xx=np.mgrid[:128,:128];mask=(xx-64)**2+(yy-64)**2<32**2
    source=np.zeros((128,128,5),'f8');source[mask,:3]=rgb;source[mask,3]=1;source[mask,4]=20
    from matplotlib import colormaps
    from visualization import srgb_to_linear
    palette=srgb_to_linear(colormaps['RdBu_r'].resampled(4097)(np.linspace(0,1,4097))[:,:3])
    optics.overlay_coverage=np.clip(optics.convolve(mask,optics.core_otf),0,1)
    image=optics.process(source,palette,s.temperature_k)
    # Pad-doubling changes only periodic-wrap contamination, not stellar flux.
    wider=Optics((128,128),test,padding=256)
    wider.overlay_coverage=np.clip(wider.convolve(mask,wider.core_otf),0,1)
    image2=wider.process(source,palette,s.temperature_k)
    report=dict(airy_unit_flux_error=abs(float(airy.sum())-1),airy_kernel_min=float(airy.min()),
        airy_first_zero_encircled_energy=ee,airy_analytic_encircled_energy=float(expected),
        moffat_unit_flux_error=abs(float(moffat.sum())-1),moffat_kernel_min=float(moffat.min()),
        moffat_encircled_energy_at_3alpha=mee,moffat_analytic_encircled_energy_at_3alpha=float(mexpected),
        spectrum_65_to_1881_nodes_max_absolute_MTF_difference=spectral_error,
        local_SED_effective_PSF_variation=local,
        synthetic_scene_padded_luminance_error=optics.full_flux_error[-1],
        synthetic_scene_pad_doubling_max_display_linear_difference=float(np.max(abs(image2-image))),
        synthetic_scene_pad_doubling_rms_display_linear_difference=float(np.sqrt(np.mean((image2-image)**2))),
        no_convection_response_in_render=True,no_temperature_amplitude_increase=True,
        known_approximation='One disk-spectrum-weighted photopic diffraction core at all surface positions; broad scattering is achromatic and integrates actual spectral RGB')
    assert abs(ee-expected)<.005 and abs(mee-mexpected)<.003
    assert airy.min()>-1e-10 and moffat.min()>-1e-10
    assert optics.full_flux_error[-1]<1e-6
    assert spectral_error<.002
    assert np.all((image>=0)&(image<=1))
    (ROOT/'validation/optics-validation.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2),flush=True)


if __name__=='__main__':main()
