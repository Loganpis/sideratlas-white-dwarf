"""Projection and fixed diagnostic display; original stellar physics is reused."""
from pathlib import Path
import json,os
ROOT=Path(__file__).resolve().parents[1]
os.environ.setdefault('MPLCONFIGDIR',str(ROOT/'.cache/matplotlib'))
os.environ.setdefault('XDG_CACHE_HOME',str(ROOT/'.cache'))
import numpy as np
from numpy.polynomial.legendre import leggauss
from matplotlib import colormaps
from PIL import Image,ImageDraw,ImageFont
from white_dwarf import Star,MODES,ColourCache,ray_map,flux_perturbation,temperature_from_flux,C


def configuration():return json.loads((ROOT/'config.json').read_text())


def srgb_to_linear(x):return np.where(x<=.04045,x/12.92,((x+.055)/1.055)**2.4)


def linear_to_srgb(x):return np.where(x<=.0031308,12.92*x,1.055*x**(1/2.4)-.055)


def camera_direction(progress,config):
    f=(1-np.cos(np.pi*np.asarray(progress)))/2
    inc=config['camera']['inclination_deg'];az=config['camera']['azimuth_deg']
    return inc[0]+f*(inc[1]-inc[0]),az[0]+f*(az[1]-az[0])


def orientation(camera,inc,az):
    a,b,c=np.moveaxis(camera,-1,0);i,p=np.deg2rad([inc,az])
    x=np.cos(i)*a-np.sin(i)*c;z=np.sin(i)*a+np.cos(i)*c
    return np.stack((np.cos(p)*x-np.sin(p)*b,np.sin(p)*x+np.cos(p)*b,z),axis=-1)


def circle_rectangle_area(x0,x1,y0,y1,radius):
    """Analytic circle/square overlap, avoiding quantized limb coverage."""
    def primitive(x,y):
        sign=np.sign(x)*np.sign(y);a=np.minimum(abs(x),radius);b=np.minimum(abs(y),radius)
        t=np.sqrt(np.maximum(0,radius*radius-b*b));lo=np.minimum(a,t)
        def integral(s):
            return .5*(s*np.sqrt(np.maximum(0,radius*radius-s*s))+radius*radius*np.arcsin(s/radius))
        return sign*(b*lo+integral(a)-integral(lo))
    area=primitive(x1,y1)-primitive(x0,y1)-primitive(x1,y0)+primitive(x0,y0)
    return np.clip(area,0,(x1-x0)*(y1-y0))


class Samples:
    """Static Schwarzschild map and exact retarded phases for packed samples."""
    def __init__(self,x,y,star,ray_grid):
        q2=(x*x+y*y)*star.redshift_factor**2
        self.mask=q2<=1
        x=x[self.mask];y=y[self.mask]
        self.mu=np.sqrt(1-q2[self.mask])
        grid,cp,dt=ray_grid
        cospsi=np.interp(self.mu,grid,cp);self.delay=np.interp(self.mu,grid,dt)*star.radius_m/C
        sinpsi=np.sqrt(1-cospsi*cospsi);rho=np.hypot(x,y)
        nx=np.divide(x,rho,out=np.zeros_like(x),where=rho!=0)*sinpsi
        ny=np.divide(y,rho,out=np.zeros_like(y),where=rho!=0)*sinpsi
        roll=np.deg2rad(-20.)
        self.a=np.cos(roll)*nx+np.sin(roll)*ny
        self.b=-np.sin(roll)*nx+np.cos(roll)*ny
        self.c=cospsi
        self.phase_cos=[np.cos(2*np.pi*self.delay/m.period_infinity_s) for m in MODES]
        self.phase_sin=[np.sin(2*np.pi*self.delay/m.period_infinity_s) for m in MODES]
        u=np.sqrt(self.mu)*128
        self.j=np.minimum(np.floor(u).astype('i4'),127);self.fmu=u-self.j

    def temperature(self,t,inc,az):
        i,p=np.deg2rad([inc,az])
        a=np.cos(i)*self.a-np.sin(i)*self.c
        z=np.sin(i)*self.a+np.cos(i)*self.c
        x=np.cos(p)*a-np.sin(p)*self.b
        h=(z,-2*x*z,-x);delta=np.zeros_like(x)
        for k,m in enumerate(MODES):
            phase=2*np.pi*t/m.period_infinity_s+m.phase_rad
            delta+=m.local_bolometric_semiamplitude*h[k]*(np.cos(phase)*self.phase_cos[k]+np.sin(phase)*self.phase_sin[k])
        return temperature_from_flux(Star(),delta)

    def radiance_y(self,temperature,cache_y):
        # Same bilinear (T,sqrt(mu)) interpolation as the original ColourCache,
        # evaluating only CIE Y rather than allocating unused RGB/XYZ channels.
        t=(temperature-11800)/10
        if np.any((t<0)|(t>40)):raise ValueError('Atmosphere cache extrapolation')
        i=np.minimum(np.floor(t).astype('i4'),39);f=t-i;j=self.j;u=self.fmu
        lo=cache_y[i,j]*(1-u)+cache_y[i,j+1]*u
        hi=cache_y[i+1,j]*(1-u)+cache_y[i+1,j+1]*u
        return lo*(1-f)+hi*f


class Tile:
    def __init__(self,row0,row1,config,star,ray_grid):
        self.row0=row0;self.row1=row1;w=config['width'];ss=config['supersample']
        self.ss=ss;self.limb_ss=config['limb_supersample'];cx,cy=np.array(config['center_fraction'])*[w,config['height']]
        radius=config['radius_fraction_of_width']*w
        yy,xx=np.mgrid[row0*ss:row1*ss,:w*ss]
        x=((xx+.5)/ss-cx)/radius;y=-((yy+.5)/ss-cy)/radius
        self.regular=Samples(x,y,star,ray_grid)
        # Only pixels intersecting the circular limb use an 8x8 subgrid.
        py,px=np.mgrid[row0:row1,:w]
        rho=np.hypot(px+.5-cx,py+.5-cy)
        self.edge=np.abs(rho-radius/star.redshift_factor)<=np.sqrt(.5)
        ey,ex=np.nonzero(self.edge);n=self.limb_ss
        apparent_radius=radius/star.redshift_factor
        self.edge_area=circle_rectangle_area(ex-cx,ex+1-cx,ey+row0-cy,ey+row0+1-cy,apparent_radius)
        dy,dx=np.mgrid[:n,:n]
        x=(ex[:,None]+(dx.ravel()+.5)/n-cx)/radius
        y=-(ey[:,None]+row0+(dy.ravel()+.5)/n-cy)/radius
        self.edge_samples=Samples(x,y,star,ray_grid)
        self.edge_counts=self.edge_samples.mask.sum(axis=1)
        self.fallback=(self.edge_counts==0)&(self.edge_area>1e-10)
        # Extremely thin slivers may contain none of the 8x8 intensity nodes.
        # Pick an interior point halfway from the nearest pixel corner to
        # its intersection with the circle, retaining the exact overlap area.
        fx=ex[self.fallback];fy=ey[self.fallback]+row0
        p0=np.stack((np.clip(cx,fx,fx+1)-cx,np.clip(cy,fy,fy+1)-cy),axis=-1)
        direction=np.stack((fx+.5-cx,fy+.5-cy),axis=-1)-p0
        aa=np.sum(direction*direction,axis=1);bb=2*np.sum(p0*direction,axis=1)
        cc=np.sum(p0*p0,axis=1)-apparent_radius**2
        root=(-bb+np.sqrt(np.maximum(0,bb*bb-4*aa*cc)))/(2*aa)
        point=p0+.5*root[:,None]*direction
        self.fallback_samples=Samples(point[:,0]/radius,-point[:,1]/radius,star,ray_grid)

    def project(self,regular_colors,edge_colors,fallback_colors):
        ss=self.ss;rows=self.row1-self.row0;w=self.edge.shape[1]
        image=np.zeros(self.regular.mask.shape+(3,),'f4')
        image[self.regular.mask]=regular_colors
        image=image.reshape(rows,ss,w,ss,3).mean(axis=(1,3))
        sparse=np.zeros(self.edge_samples.mask.shape+(3,),'f4')
        sparse[self.edge_samples.mask]=edge_colors
        mean=np.divide(sparse.sum(axis=1),self.edge_counts[:,None],out=np.zeros((len(self.edge_counts),3),'f4'),where=self.edge_counts[:,None]>0)
        mean[self.fallback]=fallback_colors
        image[self.edge]=mean*self.edge_area[:,None]
        return image


class Renderer:
    def __init__(self,config):
        self.config=config;self.star=Star();self.cache=ColourCache()
        np.testing.assert_allclose(self.cache.temperatures,np.arange(11800,12201,10))
        np.testing.assert_allclose(np.sqrt(self.cache.mu),np.linspace(0,1,129))
        self.cache_y=self.cache.xyz[...,1]
        self.center_y=float(self.cache.intensity(12000.,np.array([1.]))[0,4])
        n=config['palette_nodes'];palette=colormaps[config['palette']].resampled(n)(np.linspace(0,1,n))[:,:3]
        self.palette=srgb_to_linear(palette)
        grid=np.linspace(0,1,4097);cp,dt=ray_map(grid,self.star.compactness)
        ray_grid=(grid,cp,dt)
        self.tiles=[];h=config['height'];rows=config['tile_rows']
        # Avoid constructing empty tiles well outside the apparent stellar disk.
        cy=config['center_fraction'][1]*h;r=config['radius_fraction_of_width']*config['width']/self.star.redshift_factor
        for row0 in range(0,h,rows):
            row1=min(h,row0+rows)
            if row1<cy-r-1 or row0>cy+r+1:continue
            self.tiles.append(Tile(row0,row1,config,self.star,ray_grid))
        self.nodes,self.weights=leggauss(config['temporal_gauss_nodes']);self.weights=self.weights/2
        self.text_alpha=self.title_mask()
        self.rgb_bounds=[np.inf,-np.inf];self.temperature_bounds=[np.inf,-np.inf]

    def title_mask(self):
        cfg=self.config;w,h=cfg['width'],cfg['height'];ss=2;s=w/1080
        im=Image.new('L',(w*ss,h*ss));d=ImageDraw.Draw(im)
        def text(x,y,value,size,bold=False,anchor='lt'):
            name='lmroman12-bold.otf' if bold else 'lmroman10-regular.otf'
            font=ImageFont.truetype(str(ROOT/'fonts'/name),max(8,round(size*s*ss)))
            d.text((x*s*ss,y*s*ss),value,font=font,fill=255,anchor=anchor)
        if cfg['labels']!=['@sideratlas','NO.003','THE WHITE DWARF']:raise ValueError('Only the three approved labels')
        text(72,270,'@sideratlas',34)
        text(1008,275,'NO.003',25,anchor='rt')
        text(540,335,'THE WHITE DWARF',76,True,'mt')
        im=im.resize((w,h),Image.Resampling.LANCZOS)
        return np.asarray(im,dtype='f4')/255

    def colorize(self,samples,display_time):
        cfg=self.config;temperature=0.;y=0.
        for node,weight in zip(self.nodes,self.weights):
            time=display_time+node/(2*cfg['fps'])
            inc,az=camera_direction(time/cfg['seconds'],cfg)
            t=time*cfg['physical_seconds']/cfg['seconds']
            local=samples.temperature(t,inc,az)
            temperature=temperature+weight*local
            y=y+weight*samples.radiance_y(local,self.cache_y)
        delta=temperature-self.star.temperature_k
        if len(delta):
            self.temperature_bounds[0]=min(self.temperature_bounds[0],float(temperature.min()))
            self.temperature_bounds[1]=max(self.temperature_bounds[1],float(temperature.max()))
        scale=cfg['temperature_scale_K'];soft=cfg['asinh_softening_K']
        if np.any(abs(delta)>scale):raise ValueError('Temperature display clips')
        coord=.5*(1+np.arcsinh(delta/soft)/np.arcsinh(scale/soft))*(len(self.palette)-1)
        i=np.floor(coord).astype('i4');j=np.minimum(i+1,len(self.palette)-1);f=(coord-i)[:,None]
        colors=((1-f)*self.palette[i]+f*self.palette[j])*(cfg['exposure']*y/self.center_y)[:,None]
        if len(colors):
            self.rgb_bounds[0]=min(self.rgb_bounds[0],float(colors.min()))
            self.rgb_bounds[1]=max(self.rgb_bounds[1],float(colors.max()))
        if np.any((colors<0)|(colors>1)):raise ValueError('Linear RGB display clips')
        return colors

    def linear_frame(self,index):
        cfg=self.config;t=(index+.5)/cfg['fps']
        result=np.zeros((cfg['height'],cfg['width'],3),'f4')
        for tile in self.tiles:
            rgb=self.colorize(tile.regular,t);edge=self.colorize(tile.edge_samples,t)
            fallback=self.colorize(tile.fallback_samples,t)
            result[tile.row0:tile.row1]=tile.project(rgb,edge,fallback)
        alpha=self.text_alpha[...,None]
        # The neutral title is composited in linear light, independently of physics.
        result*=1-alpha;result+=alpha*float(srgb_to_linear(np.array(244/255)))
        return result

    def frame16(self,index):
        return np.uint16(linear_to_srgb(self.linear_frame(index))*65535+.5)


class FixedObserverPhotometry:
    def __init__(self,radial_nodes=96,azimuth_nodes=192,inc=55.,az=0.):
        self.star=Star();self.cache=ColourCache();x,w=leggauss(radial_nodes)
        self.mu=(x+1)/2;self.weights=w/2*self.mu
        phi=(np.arange(azimuth_nodes)+.5)*2*np.pi/azimuth_nodes
        cp,dt=ray_map(self.mu,self.star.compactness);s=np.sqrt(1-cp*cp)
        nx=s[:,None]*np.cos(phi);ny=s[:,None]*np.sin(phi);roll=np.deg2rad(-20.)
        camera=np.stack((np.cos(roll)*nx+np.sin(roll)*ny,-np.sin(roll)*nx+np.cos(roll)*ny,
                         np.broadcast_to(cp[:,None],nx.shape)),axis=-1)
        self.normals=orientation(camera,inc,az)
        self.delay=dt[:,None]*self.star.radius_m/C
        self.reference=float(np.sum(self.weights*self.cache.intensity(12000.,self.mu)[:,4]))

    def flux(self,t,shutter_s,nodes=2):
        x,w=leggauss(nodes);result=0.
        for node,weight in zip(x,w/2):
            temp=temperature_from_flux(self.star,flux_perturbation(self.normals,t+node*shutter_s/2,self.delay))
            y=self.cache.intensity(temp,self.mu[:,None])[...,4]
            result+=weight*np.sum(self.weights*y.mean(axis=1))/self.reference
        return float(result)
