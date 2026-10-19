#!/usr/bin/env python3
"""Measure spatial, temporal, fixed-observer and ray-map convergence."""
from pathlib import Path
import gc,json,sys,time
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'src'))
import numpy as np
from scipy.integrate import quad
from visualization import configuration,Renderer,FixedObserverPhotometry
from white_dwarf import ray_map,Star


def main():
    start=time.monotonic();out=ROOT/'validation';out.mkdir(exist_ok=True)
    cfg=configuration();cfg.update(width=270,height=480,tile_rows=48)
    a=Renderer(cfg);other=dict(cfg,temporal_gauss_nodes=4);b=Renderer(other)
    temporal=[]
    for i in [0,142,381,715,959]:
        aa=a.linear_frame(i);bb=b.linear_frame(i);error=abs(aa-bb)
        temporal.append(dict(frame=i,linear_RGB_rms=float(np.sqrt(np.mean(error**2))),linear_RGB_max=float(error.max())))
    assert max(r['linear_RGB_max'] for r in temporal)<.0002
    del a,b;gc.collect()
    cfg.update(width=540,height=960,tile_rows=48)
    a=Renderer(cfg);b=Renderer(dict(cfg,supersample=4,limb_supersample=16))
    spatial=[]
    for i in [142,480,715]:
        aa=a.linear_frame(i);bb=b.linear_frame(i);error=abs(aa-bb)
        spatial.append(dict(frame=i,width=540,height=960,
            linear_RGB_rms=float(np.sqrt(np.mean(error**2))),linear_RGB_99th_percentile=float(np.percentile(error,99)),
            linear_RGB_max=float(error.max())))
    assert max(r['linear_RGB_rms'] for r in spatial)<.0005
    del a,b;gc.collect()
    fixed=FixedObserverPhotometry();fine=FixedObserverPhotometry(144,288)
    shutter=configuration()['physical_seconds']/(32*30);photometry=[]
    for t in [0.,255.3,362.9,860.8,1291.2,1721.6]:
        v=fixed.flux(t,shutter,2);high=fine.flux(t,shutter,4)
        photometry.append(dict(observer_time_s=t,relative_CIE_Y_flux=v,
            normalized_flux_error=float(abs(v-high))))
    assert max(p['normalized_flux_error'] for p in photometry)<2e-6
    star=Star();grid=np.linspace(0,1,4097);cp,dt=ray_map(grid,star.compactness)
    # Independent adaptive integration resolves extremely grazing rays that
    # would need more fixed Gauss nodes if integrated directly one by one.
    mu=np.r_[0.,np.geomspace(1e-8,.01,20),np.linspace(.05,1,20)]
    direct_cp=[];direct_dt=[]
    for m in mu:
        b2=(1-m*m)/(1-star.compactness)
        def root(s):
            x=1-s*s
            return np.sqrt(m*m+b2*s*s*(1+x-star.compactness*(1+x+x*x)))
        # Log-spaced breakpoints explicitly resolve the narrow boundary layer
        # of a nearly tangent ray; one breakpoint can miss its small tail.
        points=np.unique(m*10.**np.arange(9)) if m>0 else None
        if points is not None:points=points[(points>0)&(points<1)]
        angle=quad(lambda s:2*np.sqrt(b2)*s/root(s),0,1,points=points,epsabs=1e-12,epsrel=1e-12)[0]
        delay=quad(lambda s:2*s*b2/(root(s)*(1+root(s))),0,1,points=points,epsabs=1e-12,epsrel=1e-12)[0]
        direct_cp.append(np.cos(angle));direct_dt.append(delay)
    rays=dict(max_cospsi_interpolation_error=float(np.max(abs(np.interp(mu,grid,cp)-direct_cp))),
        max_differential_delay_interpolation_error_s=float(np.max(abs(np.interp(mu,grid,dt)-direct_dt))*star.radius_m/299792458))
    assert rays['max_cospsi_interpolation_error']<2e-9
    assert rays['max_differential_delay_interpolation_error_s']<2e-9
    report=dict(temporal_two_vs_four_gauss_samples=temporal,
        spatial_2x_interior_8x_limb_vs_4x_interior_16x_limb=spatial,
        fixed_observer_96x192_vs_144x288_and_2_vs_4_temporal_nodes=photometry,
        ray_interpolation=rays,elapsed_s=time.monotonic()-start)
    (out/'numerical-convergence.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
