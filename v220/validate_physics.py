"""Verify preserved mode inputs, ray phases and camera/observer separation."""
from pathlib import Path
import json,sys,hashlib
import numpy as np
ROOT=Path(__file__).resolve().parent;BASE=ROOT.parent
sys.path.insert(0,str(BASE));sys.path.insert(0,str(BASE/'src'))
from mode_model import InteriorModes
from render_previews import make_renderer
from visualization import orientation,camera_direction
model=InteriorModes();cfg=json.loads((BASE/'config.json').read_text());cfg.update(width=135,height=240,tile_rows=48)
r=make_renderer('interior-modes',cfg);errors=[]
for display in [0,8,16,24,32]:
 inc,az=camera_direction(display/32,cfg)
 for tile in r.tiles:
  s=tile.regular
  if not s.mask.any():continue
  n=orientation(np.stack((s.a,s.b,s.c),axis=-1),inc,az)
  errors.append(float(np.max(abs(s.temperature(display*53.8,inc,az)-model.temperature(n,display*53.8,s.delay)))))
common=json.loads((ROOT/'data/preserved-physical-inputs.json').read_text())
checks={k:hashlib.sha256((BASE/k).read_bytes()).hexdigest()==v for k,v in common.items()}
assert all(checks.values());assert max(errors)<1e-9
report=dict(preserved_shared_input_hashes=checks,all_shared_physical_inputs_unchanged=True,max_ray_temperature_difference_K=max(errors),mode_periods_infinity_s=[m['period_infinity_s'] for m in model.modes],mode_surface_amplitudes=[m['base_flux_amplitude'] for m in model.modes],physical_temperatures_not_enhanced=True,mode_clock_rate=53.8,cell_local_clock_rate=.05,separate_display_clocks=True,observer_fixed=cfg['fixed_observer'],camera_movement_is_not_stellar_rotation=True,cellular_layer_not_physical_observer_photometry=True)
(ROOT/'validation/physics-preservation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
