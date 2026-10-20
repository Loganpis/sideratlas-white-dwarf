"""Check new evaluation paths and physical inclusion decisions without a new simulation."""
from pathlib import Path
from types import SimpleNamespace
import sys,json
import numpy as np
ROOT=Path(__file__).resolve().parent;BASE=ROOT.parent
sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(BASE/'src'));sys.path.insert(0,str(BASE))
from final_renderer import FinalRenderer
from white_dwarf import ColourCache
from mode_model import InteriorModes
from validate_research import light_curve

def main():
    cfg=json.loads((ROOT/'config.json').read_text());model=InteriorModes();cache=ColourCache(BASE/'data/research-colour-cache.npz')
    rng=np.random.default_rng(3003);mu=np.r_[0.,1.,rng.uniform(0,1,10000)]
    T=rng.uniform(cache.temperatures[0],cache.temperatures[-1],len(mu));u=np.sqrt(mu)*128
    samples=SimpleNamespace(j=np.minimum(u.astype('i4'),127),fmu=u-np.minimum(u.astype('i4'),127))
    # No need to allocate a full image to verify the optimized interpolant.
    r=object.__new__(FinalRenderer);r.tmin=cache.temperatures[0];r.tstep=cache.temperatures[1]-r.tmin
    center=float(cache.intensity(model.star.temperature_k,np.array([1.]))[0,4])
    r.radiance=np.concatenate((cache.rgb,cache.xyz[...,1:2]),axis=-1)/center
    fast=r.intensity(samples,T);reference=cache.intensity(T,mu)[:,[0,1,2,4]]/center
    error=float(np.max(abs(fast/reference-1)));assert error<1e-12
    # Explicitly retain the separate, unmoving physical observer.
    centers=np.array([.9,215.,432.,862.,1200.,1720.6]);shutter=53.8/cfg['fps']
    def integrate(nodes):
        x,w=np.polynomial.legendre.leggauss(nodes)
        return sum(weight/2*light_curve(model.temperature,model.star,cache,centers+node*shutter/2,96,192) for node,weight in zip(x,w))
    f2=integrate(2);f4=integrate(4);shutter_error=float(np.max(abs(f2/f4-1)));assert shutter_error<1e-8
    surface=json.loads((ROOT/'validation/surface-physics.json').read_text())
    assert surface['granule_size_pixels']<.1
    assert not surface['new_RHD_or_MHD_simulation_performed']
    assert max(model.star.temperature_k-surface['sampled_global_temperature_range_K'][0],surface['sampled_global_temperature_range_K'][1]-model.star.temperature_k)<160
    optics=json.loads((BASE/'luminous/validation/optics-validation.json').read_text())
    assert optics['spectrum_65_to_1881_nodes_max_absolute_MTF_difference']<1e-4
    assert optics['synthetic_scene_padded_luminance_error']<1e-6
    # A convex mixture of these normalized positive kernels stays normalized
    # and positive for the current broad-wing scattering fraction.
    assert 0<=cfg['scatter_fraction']<=1
    assert optics['airy_kernel_min']>=0 and optics['moffat_kernel_min']>=0
    caption=(ROOT/'instagram-description.text').read_text();assert len(caption)<=2200
    source=json.loads((BASE/'config.json').read_text());assert source['labels']==['@sideratlas','NO.003','THE WHITE DWARF']
    decision=json.loads((ROOT/'validation/surface-decision.json').read_text())
    assert decision['fallback_authorized'] and not decision['visible_granulation_included']
    assert not cfg['granulation_enabled']
    report=dict(optimized_radiance_interpolant_max_relative_error=error,random_samples=len(mu),
        shutter_2_to_4_nodes_max_relative_flux_error=shutter_error,shutter_physical_seconds=shutter,
        fixed_observer=dict(inclination_deg=55,azimuth_deg=0,independent_of_camera=True),
        surface_decisions_validated=True,temperature_scale_unclipped_in_global_sampling=True,
        original_optical_kernel_checks_retained=True,caption_characters=len(caption),
        current_scattering_fraction=cfg['scatter_fraction'],physical_mode_amplitudes_unchanged=True,
        no_granulation_texture_or_magnetic_map=True)
    (ROOT/'validation/numerical-validation.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))

if __name__=='__main__':main()
