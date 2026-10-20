"""Forward optical imaging and a radiometrically normalized false-color display.

Both core and scattering channels redistribute the same calculated radiation.
No positive glow is added to an unchanged source. The broad halo uses the
calculated DA spectrum, not the diagnostic temperature color palette.
"""
from pathlib import Path
import sys,json
import numpy as np
from scipy.fft import rfft2,irfft2,rfftfreq,fftfreq
from scipy.interpolate import RegularGridInterpolator

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT.parent
sys.path.insert(0,str(BASE))
sys.path.insert(0,str(BASE/'src'))
from render_previews import make_renderer
from visualization import camera_direction,linear_to_srgb,srgb_to_linear
from mode_model import ResearchAtmosphere,InteriorModes

# Luminance row of the inverse of the XYZ->linear-sRGB matrix used in B.
YROW=np.linalg.inv(np.array([[3.24096994,-1.53738318,-.49861076],
 [-.96924364,1.8759675,.04155506],[.05563008,-.20397696,1.05697151]]))[1]


def project(tile,regular,edge,fallback):
    n=regular.shape[-1];rows=tile.row1-tile.row0;w=tile.edge.shape[1]
    image=np.zeros(tile.regular.mask.shape+(n,),'f4');image[tile.regular.mask]=regular
    image=image.reshape(rows,tile.ss,w,tile.ss,n).mean(axis=(1,3))
    sparse=np.zeros(tile.edge_samples.mask.shape+(n,),'f4');sparse[tile.edge_samples.mask]=edge
    mean=np.divide(sparse.sum(axis=1),tile.edge_counts[:,None],out=np.zeros((len(tile.edge_counts),n),'f4'),where=tile.edge_counts[:,None]>0)
    mean[tile.fallback]=fallback
    image[tile.edge]=mean*tile.edge_area[:,None]
    return image


def airy_otf(frequency,first_zero):
    # Analytic incoherent circular-aperture MTF. rho=1 at D/lambda cutoff.
    rho=np.minimum(1,frequency*(np.pi/3.8317059702075125)*first_zero)
    return 2/np.pi*(np.arccos(rho)-rho*np.sqrt(np.maximum(0,1-rho*rho)))


class Optics:
    def __init__(self,shape,config,temperature=None,psf_nodes=65,padding=None):
        self.cfg=config;self.h,self.w=shape;self.scale=self.w/1080
        self.pad=round(config['padding_at_1080']*self.scale) if padding is None else padding
        self.shape=(self.h+2*self.pad,self.w+2*self.pad)
        fy=fftfreq(self.shape[0])[:,None];fx=rfftfreq(self.shape[1])[None,:]
        freq=np.hypot(fx,fy)
        star=InteriorModes().star;atmo=ResearchAtmosphere()
        self.wave=np.linspace(360,830,psf_nodes)
        wave=self.wave;flux=atmo.flux_spectrum(star.temperature_k if temperature is None else temperature,star.logg_cgs,wave*star.redshift_factor)
        ybar=np.interp(wave,atmo.cmf[:,0],atmo.cmf[:,2])
        weight=flux*ybar;weight[[0,-1]]*=.5;weight/=weight.sum()
        core=np.zeros(freq.shape,dtype='f8')
        first=config['airy_first_zero_px_at_550nm_1080']*self.scale
        for lam,wt in zip(wave,weight):core+=wt*airy_otf(freq,first*lam/550)
        core*=np.exp(-2*np.pi**2*(config['jitter_sigma_px_at_1080']*self.scale)**2*freq**2)
        # Exact continuous Fourier transform of a normalized beta=2.5 Moffat.
        assert config['moffat_beta']==2.5
        q=2*np.pi*config['moffat_alpha_px_at_1080']*self.scale*freq
        self.core_otf=core;self.wing_otf=(1+q)*np.exp(-q)
        self.overlay_coverage=1.
        self.effective_Y_wavelength_nm=float(np.sum(wave*weight))
        self.full_flux_error=[];self.crop_fractions=[]

    def convolve(self,plane,otf):
        field=np.pad(np.asarray(plane,dtype='f8'),self.pad)
        return irfft2(rfft2(field,workers=2)*otf,s=self.shape,workers=2)

    def process(self,source,palette,t0):
        # source[...,0:3] = true spectral RGB; 3=physical Y; 4=Y*deltaT.
        cfg=self.cfg;eta=cfg['scatter_fraction'];y=source[...,3]
        core_y=self.convolve(y,self.core_otf)
        core_ty=self.convolve(source[...,4],self.core_otf)
        # This is an intensity-weighted temperature diagnostic, not an
        # assertion that a telescope directly measures a resolved Teff map.
        dt=np.divide(core_ty,core_y,out=np.zeros_like(core_y),where=core_y>1e-8)
        physical_core=np.stack([self.convolve(source[...,i],self.core_otf) for i in range(3)],axis=-1)
        halo=np.stack([self.convolve(source[...,i],self.wing_otf) for i in range(3)],axis=-1)
        core_y=np.maximum(core_y,0);physical_core=np.maximum(physical_core,0);halo=np.maximum(halo,0)
        dt=np.clip(dt,-cfg['temperature_scale_K'],cfg['temperature_scale_K'])
        coord=.5*(1+np.arcsinh(dt/cfg['asinh_softening_K'])/np.arcsinh(cfg['temperature_scale_K']/cfg['asinh_softening_K']))*(len(palette)-1)
        i=np.floor(coord).astype('i4');f=coord-i
        colors=palette[i]*(1-f[...,None])+palette[np.minimum(i+1,len(palette)-1)]*f[...,None]
        chrom=colors/(colors@YROW)[...,None]
        true_chrom=np.divide(physical_core,core_y[...,None],out=np.zeros_like(physical_core),where=core_y[...,None]>1e-12)
        # Diagnostic coloring is localized with the PSF-filtered stellar
        # coverage, so scattered light outside the resolved disk retains
        # its calculated spectrum rather than the temperature-map colors.
        a=cfg['false_color_strength']*self.overlay_coverage
        if np.ndim(a):a=a[...,None]
        core=(1-eta)*core_y[...,None]*(a*chrom+(1-a)*true_chrom)
        hdr=core+eta*halo
        total=float(np.sum(hdr@YROW));original=float(np.sum(y))
        self.full_flux_error.append(abs(total/original-1))
        p=self.pad;crop=hdr[p:p+self.h,p:p+self.w]
        self.crop_fractions.append(float(np.sum(crop@YROW)/total))
        # Fixed display response, no per-frame auto exposure or normalization.
        ldr=-np.expm1(-cfg['display_exposure']*crop)
        return ldr


class LuminousRenderer:
    def __init__(self,config):
        self.cfg=config;self.factor=config['internal_scale'];w=config['preview_width']*self.factor
        cfg=json.loads((BASE/'config.json').read_text());cfg.update(width=w,height=round(w*16/9),fps=config['fps'],tile_rows=48)
        self.source=make_renderer('interior-modes',cfg)
        # Round-off can push the original fallback for a sub-pixel limb
        # sliver outside the circle. Use an inward limiting ray at the
        # same pixel azimuth; keep the analytic overlap area unchanged.
        self.repaired_limb_slivers=0
        cx,cy=np.array(cfg['center_fraction'])*[w,cfg['height']]
        radius=cfg['radius_fraction_of_width']*w
        from white_dwarf import ray_map
        grid=np.linspace(0,1,4097);cp,dt=ray_map(grid,self.source.star.compactness)
        for tile in self.source.tiles:
            if not np.all(tile.fallback_samples.mask):
                ey,ex=np.nonzero(tile.edge)
                x=(ex[tile.fallback]+.5-cx)/radius
                y=-(ey[tile.fallback]+tile.row0+.5-cy)/radius
                factor=(1-1e-12)/(self.source.star.redshift_factor*np.hypot(x,y))
                tile.fallback_samples=type(tile.regular)(x*factor,y*factor,self.source.star,(grid,cp,dt))
                self.repaired_limb_slivers+=int(np.sum(tile.fallback))
        self.optics=Optics((cfg['height'],cfg['width']),config)
        area=np.zeros((cfg['height'],cfg['width']),'f4')
        for tile in self.source.tiles:
            unit=[np.ones((int(s.mask.sum()),1),'f4') for s in [tile.regular,tile.edge_samples,tile.fallback_samples]]
            area[tile.row0:tile.row1]=project(tile,*unit)[...,0]
        self.optics.overlay_coverage=np.clip(self.optics.convolve(area,self.optics.core_otf),0,1)
        # Typography is kept out of the optical pipeline, at output resolution.
        out_cfg=dict(cfg,width=config['preview_width'],height=round(config['preview_width']*16/9))
        from visualization import Renderer
        # title_mask uses only config and fonts, so no second stellar map needed.
        title=object.__new__(Renderer);title.config=out_cfg
        self.alpha=title.title_mask()[...,None]
        self.temperature_bounds=[np.inf,-np.inf]

    def sample(self,samples,display_time):
        r=self.source;cfg=r.config;temp=0.;rgb=0.;y=0.;ty=0.
        for node,weight in zip(r.nodes,r.weights):
            time=display_time+node/(2*cfg['fps']);inc,az=camera_direction(time/cfg['seconds'],cfg)
            t=time*cfg['physical_seconds']/cfg['seconds']
            local=samples.temperature(t,inc,az)
            values=r.cache.intensity(local,samples.mu)
            rgb=rgb+weight*values[:,:3]/r.center_y
            intensity=values[:,4]/r.center_y
            y=y+weight*intensity;ty=ty+weight*intensity*(local-r.star.temperature_k)
            if len(local):
                self.temperature_bounds[0]=min(self.temperature_bounds[0],float(local.min()))
                self.temperature_bounds[1]=max(self.temperature_bounds[1],float(local.max()))
        return np.column_stack((rgb,y,ty))

    def source_fields(self,index):
        r=self.source;cfg=r.config;t=(index+.5)/cfg['fps']
        result=np.zeros((cfg['height'],cfg['width'],5),'f4')
        for tile in r.tiles:
            fields=[self.sample(s,t) for s in [tile.regular,tile.edge_samples,tile.fallback_samples]]
            result[tile.row0:tile.row1]=project(tile,*fields)
        return result

    def frame16(self,index):
        source=self.source_fields(index)
        image=self.optics.process(source,self.source.palette,self.source.star.temperature_k)
        n=self.factor;h,w=self.alpha.shape[:2]
        image=image.reshape(h,n,w,n,3).mean(axis=(1,3))
        image=image*(1-self.alpha)+self.alpha*float(srgb_to_linear(np.array(244/255)))
        assert np.all((image>=0)&(image<=1))
        return np.uint16(linear_to_srgb(image)*65535+.5)
