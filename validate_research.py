"""Numerical checks and fixed-observer diagnostics for the research previews."""
from pathlib import Path
import json,sys
import numpy as np
from numpy.polynomial.legendre import leggauss

ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'src'))
from white_dwarf import Star,ColourCache,ray_map,C,flux_perturbation,temperature_from_flux,harmonic
from mode_model import InteriorModes,ResearchAtmosphere
from convective_response import ConvectiveSurface,solve
from visualization import orientation,camera_direction


def observer_nodes(star,nr=64,np_=128):
    x,w=leggauss(nr);mu=(x+1)/2;weight=w/2*mu
    phi=(np.arange(np_)+.5)*2*np.pi/np_
    cp,dt=ray_map(mu,star.compactness)
    s=np.sqrt(1-cp*cp);nx=s[:,None]*np.cos(phi);ny=s[:,None]*np.sin(phi)
    roll=np.deg2rad(-20)
    camera=np.stack((np.cos(roll)*nx+np.sin(roll)*ny,-np.sin(roll)*nx+np.cos(roll)*ny,
                    np.broadcast_to(cp[:,None],nx.shape)),axis=-1)
    # A single fixed direction, independent of the display camera.
    normals=orientation(camera,55.,0.)
    return mu,weight,normals,dt[:,None]*star.radius_m/C


def light_curve(surface,star,cache,times,nr=64,np_=128):
    mu,w,normals,delay=observer_nodes(star,nr,np_)
    ref=float(np.sum(w*cache.intensity(star.temperature_k,mu)[...,4]))
    out=[]
    for t in times:
        temp=surface(normals,t,delay)
        y=cache.intensity(temp,mu[:,None])[...,4]
        out.append(float(np.sum(w*y.mean(axis=1))/ref))
    return np.array(out)


def main():
    model=InteriorModes();conv=ConvectiveSurface();rng=np.random.default_rng(3)
    z=rng.uniform(-1,1,80);p=rng.uniform(0,2*np.pi,80)
    n=np.stack((np.sqrt(1-z*z)*np.cos(p),np.sqrt(1-z*z)*np.sin(p),z),axis=-1)
    time,ref=solve(n,duration=432,dt=.25,storage='f8')
    _,ref2=solve(n,duration=432,dt=.5,storage='f8')
    _,terminal=solve(n,duration=432,dt=.5,padding=15000,storage='f8')
    _,constant=solve(n[:8],duration=432,dt=.5,exponent=0.,storage='f8')
    exact=np.ones_like(constant,dtype='f8');tc=np.arange(len(constant))*.5
    tau=100/model.star.redshift_factor
    for m in model.modes:
        omega=2*np.pi/m['period_infinity_s']
        exact+=m['base_flux_amplitude']*harmonic(m['l'],m['m'],n[:8])[None,:]/np.sqrt(1+(omega*tau)**2)*np.cos(
            omega*tc[:,None]+m['phase_rad']+np.arctan(omega*tau))
    queries=np.broadcast_to(n,(len(time),)+n.shape)
    interp=conv.temperature(queries,time[:,None])
    ref_temp=model.star.temperature_k*ref.astype('f8')**.25
    checks=dict(
        convective_grid_max_temperature_error_K=float(np.max(abs(interp-ref_temp))),
        convective_time_step_half_max_temperature_error_K=float(np.max(abs(model.star.temperature_k*(ref[::2].astype('f8')**.25-ref2.astype('f8')**.25)))),
        convective_extra_terminal_padding_max_flux_error=float(np.max(abs(terminal-ref2))),
        convective_constant_tau_analytic_max_flux_error=float(np.max(abs(constant-exact))),
        convective_grid_temperature_range_K=[float(model.star.temperature_k*conv.flux.min()**.25),float(model.star.temperature_k*conv.flux.max()**.25)])
    assert checks['convective_grid_max_temperature_error_K']<.25
    assert checks['convective_time_step_half_max_temperature_error_K']<.001
    assert checks['convective_extra_terminal_padding_max_flux_error']<1e-6
    assert checks['convective_constant_tau_analytic_max_flux_error']<1e-6
    times=np.linspace(.1,430.3,321)
    oldstar=Star();oldcache=ColourCache();cache=ColourCache(ROOT/'data/research-colour-cache.npz')
    oldsurface=lambda n,t,d:temperature_from_flux(oldstar,flux_perturbation(n,t,d))
    curves=[light_curve(oldsurface,oldstar,oldcache,times),
            light_curve(model.temperature,model.star,cache,times),
            light_curve(conv.temperature,model.star,cache,times)]
    np.savetxt(ROOT/'preview/fixed-observer-light-curves.csv',np.column_stack((times,*curves)),delimiter=',',
               header='observer_time_s,version_b_relative_CIE_Y,interior_modes_relative_CIE_Y,convection_sensitivity_relative_CIE_Y',comments='')
    idx=np.arange(0,len(times),16)
    refined=light_curve(model.temperature,model.star,cache,times[idx],96,192)
    checks['linear_photometry_64x128_to_96x192_max_relative_flux_error']=float(np.max(abs(refined-curves[1][idx])))
    refined_conv=light_curve(conv.temperature,model.star,cache,times[idx],96,192)
    checks['convective_photometry_64x128_to_96x192_max_relative_flux_error']=float(np.max(abs(refined_conv-curves[2][idx])))
    checks['fixed_observer']={'inclination_deg':55,'azimuth_deg':0,'independent_of_camera':True,'passband':'CIE photopic Y; not bolometric or false-color image luminance'}
    checks['peak_to_peak_flux_percent']={k:float(100*np.ptp(c)) for k,c in zip(['version_b','interior_modes','convection_sensitivity'],curves)}
    atmosphere=ResearchAtmosphere()
    mu=np.linspace(0,1,129)**2
    _,coarse=atmosphere.colour_radiance(model.star.temperature_k,model.star.logg_cgs,mu,model.star.redshift_factor,.25)
    _,fine=atmosphere.colour_radiance(model.star.temperature_k,model.star.logg_cgs,mu,model.star.redshift_factor,.125)
    checks['spectral_sampling_half_max_relative_CIE_Y_difference']=float(np.max(abs(fine[:,1]/coarse[:,1]-1)))
    (ROOT/'validation/surface-validation.json').write_text(json.dumps(checks,indent=2)+'\n')
    print(json.dumps(checks,indent=2),flush=True)


if __name__=='__main__':main()
