"""Held-out numerical checks; these are not hydrodynamic validation."""
from pathlib import Path
import sys,json
import numpy as np
from scipy.ndimage import gaussian_filter
ROOT=Path(__file__).resolve().parent;sys.path.insert(0,str(ROOT/'src'))
from cellular_convection import CellularModel,sphere_points,CellularAtlas
m=CellularModel();p=sphere_points(30000,881);reports=[]
for t in [1.23,4.57,19.21]:
 a=m.raw(p,t,32);b=m.raw(p,t,64)
 reports.append(dict(t=t,rms_difference=float(np.sqrt(np.mean((a-b)**2))),max_difference=float(abs(a-b).max())))
cal=json.loads((ROOT/'data/cellular-calibration.json').read_text())
class Star:redshift_factor=.999902894
cfg=dict(cell_atlas_latitude_nodes=1025,cell_atlas_longitude_nodes=2048,cell_local_time_step_s=.005,cell_local_seconds_per_display_second=.05)
a=CellularAtlas(cfg,Star());ts=.317
v=a.sample(p,ts,np.zeros(len(p)))
raw=m.raw(p,.05*ts/cal['local_seconds_per_model_unit']);exact=1+cal['intensity_scale']*(raw**cal['profile_power']-cal['profile_mean'])
b=CellularAtlas(dict(cfg,cell_local_time_step_s=.0025),Star());fine=b.sample(p,ts,np.zeros(len(p)))
# An independent image patch sampled at one native pixel per angular pitch.
n=320;pitch=1/(.49*1080);xx,yy=np.meshgrid((np.arange(n)-n/2)*pitch,(np.arange(n)-n/2)*pitch)
q=np.stack([np.ones_like(xx),xx,yy],axis=-1);q/=np.linalg.norm(q,axis=-1,keepdims=True);q=q.reshape(-1,3)
direct=1+cal['intensity_scale']*(m.raw(q,.05*ts/cal['local_seconds_per_model_unit'])**cal['profile_power']-cal['profile_mean'])
approx=a.sample(q,ts,np.zeros(len(q)))
# Gaussian is a conservative local proxy for the prescribed optical core;
# exact optical transfer remains checked separately in final image validation.
diff=gaussian_filter((direct-approx).reshape(n,n),1.)
image_rms=float(np.std(diff));numerical_pass=max(x['rms_difference'] for x in reports)<1e-4 and float(np.std(v-fine))<.003 and image_rms<.012
report=dict(neighbor_candidate_checks=reports,atlas_vs_direct_RMS=float(np.std(v-exact)),temporal_step_halving_RMS=float(np.std(v-fine)),intensity_RMS=float(np.std(exact)),native_patch_smoothed_absolute_RMS_error=image_rms,atlas_mean=float(np.mean(v)),atlas_relative_RMS=float(np.std(v)/np.mean(v)),numerical_checks_passed=numerical_pass,interpretation='Numerical checks of a statistical surrogate, not RHD validation; atlas smoothing explicitly measured')
(ROOT/'validation/cellular-numerics.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2),flush=True)
if not numerical_pass:raise ValueError('Numerical checks failed')
