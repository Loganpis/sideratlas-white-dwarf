"""Fixed diagnostic contrast, applied only after normalized physical imaging.
The displayed core is false color and enhanced luminance, not observed light.
Halo remains the calculated DA spectrum through the same normalized PSF.
"""
import numpy as np
from luminous_render import Optics,YROW
from scipy.fft import rfft2,irfft2

class SurfaceOptics(Optics):
 def process(self,source,palette,t0):
  cfg=self.cfg;eta=cfg['scatter_fraction'];y=source[...,3]
  if not hasattr(self,'core32'):
   self.core32=self.core_otf.astype('f4');self.wing32=self.wing_otf.astype('f4')
  physical_core=np.empty(self.shape+(3,),'f4');halo=np.empty_like(physical_core)
  for channel in range(3):
   ft=rfft2(np.pad(source[...,channel].astype('f4'),self.pad),workers=2)
   physical_core[...,channel]=irfft2(ft*self.core32,s=self.shape,workers=2)
   halo[...,channel]=irfft2(ft*self.wing32,s=self.shape,workers=2)
  # XYZ/sRGB are linearly related: derive Y from the same filtered spectrum.
  physical_core=np.maximum(physical_core,0);halo=np.maximum(halo,0)
  core_y=physical_core@YROW
  ft=rfft2(np.pad(source[...,4].astype('f4'),self.pad),workers=2)
  ty=irfft2(ft*self.core32,s=self.shape,workers=2)
  dt=np.divide(ty,core_y,out=np.zeros_like(core_y),where=core_y>1e-8)
  physical=(1-eta)*physical_core+eta*halo
  original=float(y.sum());total=float((physical@YROW).sum())
  self.full_flux_error.append(abs(total/original-1));p=self.pad
  self.crop_fractions.append(float((physical[p:p+self.h,p:p+self.w]@YROW).sum()/total))
  # Fixed temperature diagnostic; no per-frame histogram or auto exposure.
  u=np.arcsinh(np.clip(dt,-cfg['temperature_scale_K'],cfg['temperature_scale_K'])/cfg['asinh_softening_K'])/np.arcsinh(cfg['temperature_scale_K']/cfg['asinh_softening_K'])
  coord=.5*(u+1)*(len(palette)-1);i=coord.astype('i4');f=coord-i
  color=palette[i]*(1-f[...,None])+palette[np.minimum(i+1,len(palette)-1)]*f[...,None]
  chrom=color/(color@YROW)[...,None]
  true=np.divide(physical_core,core_y[...,None],out=np.zeros_like(physical_core),where=core_y[...,None]>1e-12)
  coverage=self.overlay_coverage;a=cfg['false_color_strength']*coverage
  display_chrom=a[...,None]*chrom+(1-a[...,None])*true
  # Explicit visualization enhancement of pulsation visibility; the model's
  # radiance, temperature amplitudes, and separate observer curve are unchanged.
  gain=np.exp(cfg['display_temperature_luminance_gain']*u*coverage)
  hdr=(1-eta)*core_y[...,None]*display_chrom*gain[...,None]+eta*halo
  crop=hdr[p:p+self.h,p:p+self.w]
  Y=crop@YROW
  mapped=cfg['display_exposure']*Y/(1+cfg['display_exposure']*Y)
  rgb=np.divide(crop,Y[...,None],out=np.zeros_like(crop),where=Y[...,None]>1e-15)*mapped[...,None]
  # Compress only chroma toward neutral at constant mapped luminance to fit
  # the RGB gamut. This avoids independent channel clipping/white clipping.
  delta=rgb-mapped[...,None]
  positive=np.max(delta,axis=-1);negative=-np.min(delta,axis=-1)
  ap=np.divide(1-mapped,positive,out=np.ones_like(mapped),where=positive>1e-15)
  an=np.divide(mapped,negative,out=np.ones_like(mapped),where=negative>1e-15)
  a=np.minimum(1,np.minimum(ap,an))
  return np.clip(mapped[...,None]+a[...,None]*delta,0,1)
