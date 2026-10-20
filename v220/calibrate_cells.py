"""Calibrate a statistical visualization surrogate; not a new DA RHD model."""
from pathlib import Path
import sys,json,time
import numpy as np
from scipy.optimize import brentq
ROOT=Path(__file__).resolve().parent;BASE=ROOT.parent;sys.path.insert(0,str(ROOT/'src'))
from cellular_convection import CellularModel,generate_catalog,sphere_points

def correlation(model,points,times,power):
 a=np.array([model.raw(points,t)**power for t in times]);a-=a.mean(axis=1,keepdims=True)
 var=np.mean(a*a);dt=np.mean(np.diff(times));ac=np.array([np.mean(a[:-j]*a[j:])/var for j in range(1,len(a)//2)])
 crosses=np.flatnonzero(ac<np.exp(-1));
 if not len(crosses):raise ValueError('No measured surrogate correlation decay')
 j=int(crosses[0]);prev=1 if j==0 else ac[j-1];decay=(j+(prev-np.exp(-1))/(prev-ac[j]))*dt
 return float(decay),ac.tolist()

def main():
 begin=time.monotonic();path=ROOT/'data/cellular-catalog.npz'
 if not path.exists():generate_catalog(path)
 model=CellularModel();points=sphere_points(32768);times=np.linspace(1,12,16)
 raw=np.concatenate([model.raw(points,t) for t in times])
 # DA bright-area values at logg8: 53.8% at11005K,55.8% at11529K.
 # Neighbor interpolation is a morphology constraint, not exact DA imagery.
 target_bright=float(np.interp(11290.02004,[11005,11529],[.538,.558]))
 def bright(power):
  x=raw**power;return np.mean(x>x.mean())
 candidates=np.geomspace(.12,12,81);power=float(candidates[np.argmin([abs(bright(p)-target_bright) for p in candidates])])
 shaped=raw**power;mean=float(shaped.mean());rms=float(shaped.std());target=.17267912516280088;scale=target/rms
 assert 1-scale*mean>0
 decay,ac=correlation(model,sphere_points(4096,224),np.linspace(2,9,141),power)
 unit=.11047357752955808/decay
 # Independent epochs/directions are withheld from fitting.
 val=np.array([1+scale*(model.raw(sphere_points(32768,225),t)**power-mean) for t in np.linspace(16,28,13)])
 val_rms=np.std(val,axis=1)/np.mean(val,axis=1);val_bright=np.mean(val>val.mean(axis=1,keepdims=True),axis=1)
 vd,vac=correlation(model,sphere_points(4096,226),np.linspace(18,25,141),power)
 # Tangent-plane spatial spectrum at six independent local patches/times.
 n=384;span=.8;x=(np.arange(n)+.5)/n*span-span/2;xx,yy=np.meshgrid(x,x);q=np.stack([np.ones_like(xx),xx,yy],axis=-1);q/=np.linalg.norm(q,axis=-1,keepdims=True)
 spectral=[]
 freq=np.hypot(np.fft.fftfreq(n)[:,None],np.fft.fftfreq(n)[None,:]);bins=np.rint(freq*n).astype(int)
 window=np.outer(np.hanning(n),np.hanning(n))
 for t in [3,6,9,18,21,24]:
  image=model.raw(q.reshape(-1,3),t).reshape(n,n)**power;image=(image-image.mean())*window
  p=np.abs(np.fft.fft2(image))**2;spec=np.bincount(bins.ravel(),weights=p.ravel());spec*=np.arange(len(spec));spec[:2]=0
  peak=int(np.argmax(spec));spectral.append(span/peak)
 wavelength=float(np.median(spectral));mag=wavelength*9018.133761753139/.8522720853480057
 report=dict(model='Finite-lived drifting multiplicatively weighted spherical Voronoi intensity surrogate',hydrodynamic_solution=False,failed_RHD_outputs_used=False,
  profile_power=power,profile_mean=mean,intensity_scale=scale,target_bolometric_intensity_RMS=target,target_bright_area_fraction=target_bright,
  calibration_decay_model_units=decay,local_seconds_per_model_unit=unit,target_approx_decay_local_s=.11047357752955808,
  validation_RMS_mean=float(val_rms.mean()),validation_RMS_range=[float(val_rms.min()),float(val_rms.max())],validation_bright_area_mean=float(val_bright.mean()),validation_decay_local_s=vd*unit,
  minimum_possible_intensity=1-scale*mean,measured_angular_characteristic_scale_rad=wavelength,local_patch_angular_scales_rad=spectral,spatial_magnification=mag,reference_granule_size_km=.8522720853480057,
  statistical_checks_passed=bool(abs(val_rms.mean()/target-1)<.1 and abs(vd*unit/.11047357752955808-1)<.25 and abs(val_bright.mean()-target_bright)<.05),
  constraints='Neighbor DA RHD bolometric vertical intensity contrast/size; empirical decay estimate; morphology, birth process and drift prescribed',
  limitations=['No mass/momentum/energy evolution or validated DA convection','Grey bolometric intensity proxy, not local Teff or optical cell spectra','Magnification reduces visible cell count; not physical disk photometry','No nonadiabatic mode/convection coupling or fluid velocities claimed'],elapsed_s=time.monotonic()-begin)
 (ROOT/'data/cellular-calibration.json').write_text(json.dumps(report,indent=2)+'\n');(ROOT/'validation/cellular-statistics.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2),flush=True)
 if not report['statistical_checks_passed']:raise ValueError('Statistical calibration failed')
if __name__=='__main__':main()
