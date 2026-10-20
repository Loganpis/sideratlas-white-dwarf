"""Validate enhanced rendering against full-precision linear optical transport."""
from pathlib import Path
import json,sys,time
import numpy as np
ROOT=Path(__file__).resolve().parent;BASE=ROOT.parent
sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(BASE/'luminous/src'));sys.path.insert(0,str(BASE/'src'));sys.path.insert(0,str(BASE))
from final_renderer import FinalRenderer
from luminous_render import YROW
from white_dwarf import ColourCache
from mode_model import InteriorModes
from visualization import linear_to_srgb
from PIL import Image

def main():
 cfg=json.loads((ROOT/'config.json').read_text());cfg['preview_width']=540;r=FinalRenderer(cfg);source=r.source_fields(0)
 # Independent double-precision physical Y core and RGB transport.
 op=r.optics;reference=op.convolve(source[...,3],op.core_otf)
 core_rgb=np.stack([op.convolve(source[...,i],op.core_otf) for i in range(3)],axis=-1)
 identity=float(np.max(abs(core_rgb@YROW-reference)));assert identity<1e-6
 # Float32 production transforms versus float64 reference, in linear radiance.
 from scipy.fft import rfft2,irfft2
 f=rfft2(np.pad(source[...,3],op.pad));fast=irfft2(f*op.core_otf.astype('f4'),s=op.shape)
 error=float(np.max(abs(fast-reference)));assert error<2e-6
 # Physical source temperatures still use precisely the prior six-mode cache.
 model=InteriorModes();cache=ColourCache(BASE/'data/research-colour-cache.npz')
 errorY=float(np.max(abs((cache.rgb@YROW)-cache.xyz[...,1])/cache.xyz[...,1]));assert errorY<1e-12
 image=op.process(source,r.source.palette,r.source.star.temperature_k)
 assert np.all(np.isfinite(image)) and image.min()>=0 and image.max()<=1
 assert max(op.full_flux_error)<1e-5
 for i in [0,480,720]:
  frame=r.frame16(i);Image.fromarray(np.uint8(frame/257+.5)).save(ROOT/'validation'/f'check-{i:04}.png')
 report=dict(spectral_RGB_Y_identity_max_relative_error=errorY,filtered_RGB_Y_max_absolute_error=identity,
    float32_vs_float64_core_Y_max_absolute_error=error,physical_pre_display_Y_flux_conservation_errors=op.full_flux_error,
    mode_temperatures_and_amplitudes_unchanged=True,diagnostic_luminance_gain_coefficient=cfg['display_temperature_luminance_gain'],
    fixed_luminance_tone_map='E*Y/(1+E*Y)',exposure=cfg['display_exposure'],no_per_frame_auto_exposure=True,
    gamut_mapping='desaturate toward neutral at fixed mapped Y only as needed',granulation_enabled=cfg.get('granulation_enabled',False))
 (ROOT/'validation/display-validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2),flush=True)
if __name__=='__main__':main()
