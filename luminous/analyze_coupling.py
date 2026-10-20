"""Quantify the model-to-atmosphere link and unresolved nonadiabatic freedom."""
from pathlib import Path
import sys,json
import numpy as np
import h5py
from numpy.polynomial.legendre import leggauss
ROOT=Path(__file__).resolve().parent;BASE=ROOT.parent
sys.path.insert(0,str(BASE/'src'));sys.path.insert(0,str(BASE))
from mode_model import InteriorModes,ResearchAtmosphere
from white_dwarf import ColourCache,harmonic
from validate_research import observer_nodes


def summaries(run):
    with h5py.File(ROOT/'calculations'/run/'nonadiabatic.h5') as f:
        return {(int(l),int(n)):complex(nu['re'],nu['im']) for l,n,nu in zip(f['l'][...],f['n_pg'][...],f['freq'][...])}


def f_parameter(run,l,n):
    path=ROOT/'calculations'/run/f'mode.{l}.{n}_pg.h5'
    with h5py.File(path) as f:
        val=lambda k:complex(f[k]['re'][-1],f[k]['im'][-1])
        return (val('lag_L')-2*val('xi_r'))/val('xi_r')


def main():
    model=InteriorModes();star=model.star
    cache=ColourCache(BASE/'data/research-colour-cache.npz')
    mu,w,normals,delay=observer_nodes(star,96,192)
    equilibrium=cache.intensity(star.temperature_k,mu)
    h=2.5
    derivative=(cache.intensity(star.temperature_k+h,mu)-cache.intensity(star.temperature_k-h,mu))/(2*h)
    response=star.temperature_k/4*derivative[:,4]
    reference=np.sum(w*equilibrium[:,4])
    cases={s:summaries('gsm-frozen-'+s+'-fine') for s in ['1','4']}
    coarse={s:summaries('gsm-frozen-'+s) for s in ['1','4']}
    records=[]
    for m in model.modes:
        l,n=m['l'],m['n_pg'];key=(l,n);omega=2*np.pi/m['period_infinity_s']
        spatial=harmonic(l,m['m'],normals)
        visibility=np.sum(w[:,None]*response[:,None]*spatial*np.exp(-1j*omega*delay))/normals.shape[1]/reference
        f1=f_parameter('gsm-frozen-1-fine',l,n);f4=f_parameter('gsm-frozen-4-fine',l,n)
        one=dict(l=l,n_pg=n,m=m['m'],period_GYRE_s=m['period_GYRE_s'],
            surface_flux_amplitude_prescribed=m['base_flux_amplitude'],
            photopic_visibility_per_unit_local_bolometric_flux=[float(visibility.real),float(visibility.imag)],
            predicted_linear_photopic_semiamplitude_percent=float(100*m['base_flux_amplitude']*abs(visibility)),
            frozen_surface_f_1=[f1.real,f1.imag],frozen_surface_f_4=[f4.real,f4.imag],
            frozen_f_magnitude_ratio_1_over_4=float(abs(f1/f4)),
            frozen_f_phase_difference_deg=float(np.rad2deg(np.angle(f1/f4))),
            nonadiabatic_frequency_Hz={s:[cases[s][key].real,cases[s][key].imag] for s in cases},
            nonadiabatic_frequency_resolution_difference_Hz={s:abs(cases[s][key]-coarse[s][key]) for s in cases})
        records.append(one)
    # SED/limb response is calculated, not replaced by a blackbody derivative.
    atmo=ResearchAtmosphere();sample_mu=np.array([.02,.1,.25,.5,1.])
    _,lo=atmo.colour_radiance(star.temperature_k-h,star.logg_cgs,sample_mu,star.redshift_factor)
    _,hi=atmo.colour_radiance(star.temperature_k+h,star.logg_cgs,sample_mu,star.redshift_factor)
    _,eq=atmo.colour_radiance(star.temperature_k,star.logg_cgs,sample_mu,star.redshift_factor)
    dy=star.temperature_k*(hi[:,1]-lo[:,1])/(2*h*eq[:,1])
    # Recover the original adiabatic spectrum under a format conversion.
    with h5py.File(ROOT/'calculations/gsm-frozen-1/adiabatic.h5') as f:
        ad={(int(l),int(n)):float(v['re']) for l,n,v in zip(f['l'][...],f['n_pg'][...],f['freq'][...])}
    with h5py.File(BASE/'calculations/coarse/summary.h5') as f:
        old={(int(l),int(n)):float(v['re']) for l,n,v in zip(f['l'][...],f['n_pg'][...],f['freq'][...])}
    errors=[abs(ad[(m['l'],m['n_pg'])]/old[(m['l'],m['n_pg'])]-1) for m in model.modes]
    report=dict(modes=records,format_conversion_max_relative_adiabatic_frequency_difference=max(errors),
        intensity_response=dict(mu=sample_mu.tolist(),dln_Y_dln_T=dy.tolist()),
        nonadiabatic_status='Diagnostic only; none of these flux eigenfunctions, growth rates or phases is used in the preview',
        assumptions=['GSM 1.10 freezes background cooling coefficient c_egv to zero',
          'Frozen convective transport is inadequate to establish DAV driving',
          'No calibrated time-dependent-convection closure or nonlinear saturated excitation is available',
          'Surface-flux normalization, mode selection, m assignments and phases therefore remain prescribed'],
        atmosphere_status='Retained hydrostatic LTE DA spectra and DA-3D broadband angular fits; exact monochromatic intensities for a matching grid were not publicly available in the inspected sources')
    assert max(errors)<1e-6
    (ROOT/'validation/coupling-audit.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
