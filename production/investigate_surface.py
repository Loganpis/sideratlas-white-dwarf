"""Resolution audit of published DA RHD granulation, not a new RHD simulation."""
from pathlib import Path
import sys,json
import numpy as np
ROOT=Path(__file__).resolve().parent;BASE=ROOT.parent
sys.path.insert(0,str(BASE/'src'))
from mode_model import InteriorModes
from white_dwarf import harmonic

def main():
    model=InteriorModes();star=model.star;cfg=json.loads((ROOT/'config.json').read_text())
    # Tremblay et al. 2013, arXiv:1307.2810, Table 1. Published values,
    # not a resampled or invented granulation realization.
    rows=[
      dict(teff_K=10938,logg=7.5,log_size_cm=5.30,intensity_rms_percent=19.2,Mach=.770,log_Hp_cm=4.54,log_density_cgs=-6.68),
      dict(teff_K=11498,logg=7.5,log_size_cm=5.59,intensity_rms_percent=19.9,Mach=.727,log_Hp_cm=4.60,log_density_cgs=-6.84),
      dict(teff_K=11005,logg=8.,log_size_cm=4.86,intensity_rms_percent=16.6,Mach=.598,log_Hp_cm=4.03,log_density_cgs=-6.27),
      dict(teff_K=11529,logg=8.,log_size_cm=4.96,intensity_rms_percent=17.7,Mach=.693,log_Hp_cm=4.07,log_density_cgs=-6.47),
      dict(teff_K=10997,logg=8.5,log_size_cm=4.28,intensity_rms_percent=13.4,Mach=.446,log_Hp_cm=3.51,log_density_cgs=-5.84),
      dict(teff_K=11490,logg=8.5,log_size_cm=4.33,intensity_rms_percent=14.3,Mach=.522,log_Hp_cm=3.55,log_density_cgs=-6.02)]
    keys=['log_size_cm','intensity_rms_percent','Mach','log_Hp_cm','log_density_cgs']
    def interpolate(temperature,key):
        gravities=[7.5,8.,8.5];vals=[]
        for g in gravities:
            pair=[r for r in rows if r['logg']==g]
            vals.append(np.interp(temperature,[r['teff_K'] for r in pair],[r[key] for r in pair]))
        return float(np.interp(star.logg_cgs,gravities,vals))
    est={key:interpolate(star.temperature_k,key) for key in keys}
    size=10**est['log_size_cm']/1e5;hp=10**est['log_Hp_cm'];gravity=10**star.logg_cgs
    pitch=star.radius_m/1000/(.49*cfg['preview_width'])
    r0=cfg['airy_first_zero_px_at_550nm_1080'];fc=3.8317059702075125/(np.pi*r0)
    # Eq. 16 is only an order-of-magnitude empirical fit (~30% scatter,
    # excluding the hottest thin-convection cases), not an exact local clock.
    lifetime=2.08/gravity*(star.temperature_k-300*star.logg_cgs)**1.75*10**(-.2)
    # Gamma1 is not tabulated with these RHD means. Report a clearly
    # conditional range, not a falsely precise calculated RHD velocity.
    velocity=np.sqrt(np.array([1.,5/3])*gravity*hp)*est['Mach']/1e5
    sampled_sizes=[10**interpolate(t,'log_size_cm')/1e5 for t in [star.temperature_k-160,star.temperature_k+160]]
    # Check the whole physical interval using independent spherical samples.
    z=1-2*(np.arange(4096)+.5)/4096;p=np.arange(4096)*np.pi*(3-np.sqrt(5))
    normals=np.column_stack((np.sqrt(1-z*z)*np.cos(p),np.sqrt(1-z*z)*np.sin(p),z))
    times=np.linspace(0,1721.6,2049);basis=np.array([harmonic(m['l'],m['m'],normals) for m in model.modes])
    low=np.inf;high=-np.inf
    for t in np.array_split(times,17):
        coeff=np.array([m['base_flux_amplitude']*np.cos(2*np.pi*t/m['period_infinity_s']+m['phase_rad']) for m in model.modes])
        temperature=star.temperature_k*(1+coeff.T@basis)**.25
        low=min(low,float(temperature.min()));high=max(high,float(temperature.max()))
    assert max(star.temperature_k-low,high-star.temperature_k)<cfg['temperature_scale_K']
    report=dict(source='https://arxiv.org/abs/1307.2810',source_table='Table 1',source_rows=rows,
        interpolation='Linear in Teff and logg; logarithmic table columns interpolated as logarithms; neighbor-model scale estimate, not a matched new RHD calculation',
        reference=dict(Teff_K=star.temperature_k,logg=star.logg_cgs,radius_km=star.radius_m/1000),
        estimated_RHD_quantities=est,granule_size_km=size,size_range_over_fixed_temperature_scale_km=sampled_sizes,
        disk_center_surface_pitch_km_per_pixel=pitch,granule_size_pixels=size/pitch,
        diffraction_cutoff_cycles_per_pixel_at_550nm=fc,
        shortest_transmitted_period_km_at_550nm=pitch/fc,
        approximate_decay_time_s=lifetime,decay_time_status='Eq.16 empirical order-of-magnitude estimate, not a measured mode-dependent response',
        conditional_RMS_velocity_km_s=velocity.tolist(),velocity_status='Mach * sqrt(Gamma1 * g * Hp), conditional on Gamma1 in [1,5/3]; RHD Gamma1 is not supplied in Table 1',
        radiation_temperature_contrast_proxy_K=star.temperature_k*est['intensity_rms_percent']/400,
        contrast_status='Published bolometric vertical intensity RMS; proxy delta Trad/T = delta I/(4I) is not a local pulsational Teff or optical contrast and is NOT added to the movie',
        physical_shutter_s=53.8/cfg['fps'],
        sampled_global_temperature_range_K=[low,high],
        granulation_decision='Unresolved; no cell texture, stochastic flicker or enlarged granular structures added; no spatially resolved RHD realization claimed',
        convection_decision='Retained mean atmosphere treatment and DA-3D broadband limb fits; no validated matched time-dependent convection response available',
        magnetic_decision='Nonmagnetic foundation retained; no field geometry/strength or spot contrast computed for this star, and unchanged nonmagnetic modes cannot justify imposed magnetic spots',
        magnetic_references=['https://arxiv.org/abs/1509.05398','https://arxiv.org/abs/1710.02151','https://arxiv.org/abs/2410.20557'],
        new_RHD_or_MHD_simulation_performed=False)
    (ROOT/'validation/surface-physics.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))

if __name__=='__main__':main()
