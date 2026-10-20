"""Reuse the validated luminous renderer; evaluate its identical LUT efficiently."""
from pathlib import Path
import sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT.parent
sys.path.insert(0,str(BASE/'luminous/src'))
from luminous_render import LuminousRenderer
from visualization import camera_direction

class FinalRenderer(LuminousRenderer):
    def __init__(self,config):
        super().__init__(config)
        r=self.source
        # Four required radiance channels, with a constant normalization.
        # Same bilinear interpolation in Teff and sqrt(mu) as ColourCache.
        self.radiance=np.concatenate((r.cache.rgb,r.cache.xyz[...,1:2]),axis=-1)/r.center_y
        self.tmin=r.cache.temperatures[0];self.tstep=r.cache.temperatures[1]-self.tmin

    def intensity(self,samples,temperature):
        q=(temperature-self.tmin)/self.tstep
        if np.any((q<0)|(q>len(self.radiance)-1)):raise ValueError('Atmosphere extrapolation')
        i=np.minimum(np.floor(q).astype('i4'),len(self.radiance)-2)
        f=(q-i)[:,None];j=samples.j;u=samples.fmu[:,None]
        lo=self.radiance[i,j]*(1-u)+self.radiance[i,j+1]*u
        hi=self.radiance[i+1,j]*(1-u)+self.radiance[i+1,j+1]*u
        return lo*(1-f)+hi*f

    def sample(self,samples,display_time):
        if not np.any(samples.mask):return np.empty((0,5))
        r=self.source;cfg=r.config;out=np.zeros((len(samples.mu),5))
        for node,weight in zip(r.nodes,r.weights):
            time=display_time+node/(2*cfg['fps']);inc,az=camera_direction(time/cfg['seconds'],cfg)
            t=time*cfg['physical_seconds']/cfg['seconds'];local=samples.temperature(t,inc,az)
            if np.max(abs(local-r.star.temperature_k))>self.cfg['temperature_scale_K']:
                raise ValueError('Fixed temperature scale would clip the source')
            v=self.intensity(samples,local);out[:,:4]+=weight*v
            out[:,4]+=weight*v[:,3]*(local-r.star.temperature_k)
            self.temperature_bounds[0]=min(self.temperature_bounds[0],float(local.min()))
            self.temperature_bounds[1]=max(self.temperature_bounds[1],float(local.max()))
        return out
