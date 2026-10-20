"""Companion physical light curve for a single fixed observer, no plotted view."""
from pathlib import Path
import sys,json
import numpy as np
ROOT=Path(__file__).resolve().parent;BASE=ROOT.parent
sys.path.insert(0,str(BASE/'src'));sys.path.insert(0,str(BASE))
from mode_model import InteriorModes
from white_dwarf import ColourCache
from validate_research import light_curve
from visualization import camera_direction

def main():
    config=json.loads((ROOT/'config.json').read_text());model=InteriorModes();star=model.star
    cache=ColourCache(BASE/'data/research-colour-cache.npz');fps=config['fps'];n=fps*config['preview_seconds']
    display=(np.arange(n)+.5)/fps;physical=display*53.8;shutter=53.8/fps
    nodes,weights=np.polynomial.legendre.leggauss(2)
    flux=np.zeros(n)
    for node,weight in zip(nodes,weights):
        flux+=weight/2*light_curve(model.temperature,star,cache,physical+node*shutter/2,96,192)
    np.savetxt(ROOT/'output/fixed-observer-light-curve.csv',np.column_stack((display,physical,flux)),delimiter=',',
        header='display_time_s,observer_time_s,relative_photopic_Y',comments='',fmt='%.12g')
    source=json.loads((BASE/'config.json').read_text());inc,az=camera_direction(display/32,source)
    np.savetxt(ROOT/'output/camera-schedule.csv',np.column_stack((display,inc,az)),delimiter=',',
        header='display_time_s,camera_inclination_deg,camera_azimuth_deg',comments='',fmt='%.12g')
    report=dict(samples=n,observer_inclination_deg=55,observer_azimuth_deg=0,
        peak_to_peak_percent=float(np.ptp(flux)*100),relative_Y_min=float(flux.min()),relative_Y_max=float(flux.max()),
        photometry='Physical DA atmosphere CIE Y with retarded phases and two shutter quadrature nodes; no display palette, optics or camera scan',
        normalization='Equilibrium star at identical fixed inclination/azimuth and radius',
        physical_time_speedup=53.8)
    (ROOT/'validation/photometry.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))

if __name__=='__main__':main()
