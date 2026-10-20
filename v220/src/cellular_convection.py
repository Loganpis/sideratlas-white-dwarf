"""Statistically constrained spherical cellular surrogate, NOT an RHD solution.

Finite-lived, drifting weighted Voronoi granules. DA literature constrains
bolometric contrast, characteristic length and correlation time; cell topology,
profile, birth process and drift are prescribed. No failed RHD data are read.
"""
from pathlib import Path
from collections import OrderedDict
import json
import numpy as np
from scipy.spatial import cKDTree
from numba import njit
ROOT=Path(__file__).resolve().parents[1]

@njit(cache=True)
def profile(dist,index,weight,spacing,lane):
 out=np.empty(len(dist),np.float32)
 for i in range(len(dist)):
  a=1e20;b=1e20
  for j in range(dist.shape[1]):
   s=dist[i,j]**2/weight[index[i,j]]
   if s<a:b=a;a=s
   elif s<b:b=s
  gap=(b-a)/(np.sqrt(a)+np.sqrt(b)+1e-20)
  out[i]=.8*(-np.expm1(-gap/(lane*spacing)))+.2*np.exp(-.6*a/(spacing*spacing))
 return out

def sphere_points(n,seed=223):
 rng=np.random.default_rng(seed);z=rng.uniform(-1,1,n);p=rng.uniform(0,2*np.pi,n);s=np.sqrt(1-z*z)
 return np.column_stack((s*np.cos(p),s*np.sin(p),z))

def generate_catalog(path,active=8192,seed=220003):
 rng=np.random.default_rng(seed);life_mean=3.;rate=active/life_mean
 # Long stationary burn-in; finite supported time interval recorded below.
 birth=-15+np.cumsum(rng.exponential(1/rate,int(rate*66)))
 birth=birth[birth<50];life=rng.lognormal(np.log(life_mean)-.5*.3**2,.3,len(birth))
 pos=sphere_points(len(birth),seed+1);tan=rng.normal(size=pos.shape);tan-=np.sum(tan*pos,axis=1)[:,None]*pos;tan/=np.linalg.norm(tan,axis=1)[:,None]
 spacing=np.sqrt(4*np.pi/active)
 omega=spacing*rng.uniform(.12,.24,len(birth))
 np.savez_compressed(path,birth=birth.astype('f4'),life=life.astype('f4'),position=pos.astype('f4'),tangent=tan.astype('f4'),omega=omega.astype('f4'),active_mean=active,seed=seed,supported_dimensionless_time=[-5.,35.])

class CellularModel:
 def __init__(self,path=None):
  d=np.load(path or ROOT/'data/cellular-catalog.npz');self.birth=d['birth'];self.life=d['life'];self.pos=d['position'];self.tangent=d['tangent'];self.omega=d['omega'];self.spacing=np.sqrt(4*np.pi/int(d['active_mean']))
  self.lane=.15
 def state(self,t):
  if not -5<=t<=35:raise ValueError('Cell catalog outside supported time; no temporal wrapping')
  age=t-self.birth;active=(age>0)&(age<self.life);age=age[active];phase=np.pi*age/self.life[active]
  weight=np.maximum(np.sin(phase)**2,1e-10)
  angle=self.omega[active]*age
  pos=self.pos[active]*np.cos(angle)[:,None]+self.tangent[active]*np.sin(angle)[:,None]
  return cKDTree(pos),weight
 def raw(self,points,t,k=32):
  tree,w=self.state(float(t));dist,index=tree.query(points,k=k,workers=1)
  return profile(dist,index,w,self.spacing,self.lane)

class CellularAtlas:
 def __init__(self,cfg,star):
  self.cfg=cfg;self.star=star;self.model=CellularModel();self.cal=json.loads((ROOT/'data/cellular-calibration.json').read_text())
  if not self.cal['statistical_checks_passed']:raise ValueError('Statistical surrogate not accepted for display')
  self.rows=cfg['cell_atlas_latitude_nodes'];self.cols=cfg['cell_atlas_longitude_nodes']
  lat=np.linspace(-np.pi/2,np.pi/2,self.rows);lon=np.arange(self.cols)*2*np.pi/self.cols
  c=np.cos(lat);self.points=np.stack(np.broadcast_arrays(c[:,None]*np.cos(lon),c[:,None]*np.sin(lon),np.sin(lat)[:,None]),axis=-1).reshape(-1,3).astype('f4');self.area_weights=c[:,None]
  self.cache=OrderedDict();self.step=cfg['cell_local_time_step_s']
 def atlas(self,k):
  if k not in self.cache:
   t=k*self.step/self.cal['local_seconds_per_model_unit'];raw=np.concatenate([self.model.raw(self.points[j:j+262144],t) for j in range(0,len(self.points),262144)])
   a=1+self.cal['intensity_scale']*(raw**self.cal['profile_power']-self.cal['profile_mean'])
   image=a.reshape(self.rows,self.cols)
   # Preserve the spherical mean of the mean-emission model; not an observer
   # exposure adjustment or a prediction of real whole-star granular flicker.
   image/=np.sum(image*self.area_weights)/(self.area_weights.sum()*self.cols)
   if image.min()<=0:raise ValueError('Cell surrogate intensity nonpositive')
   self.cache[k]=image.astype('f4')
   while len(self.cache)>20:self.cache.popitem(last=False)
  self.cache.move_to_end(k);return self.cache[k]
 def sample(self,normals,display_time,delay):
  t=self.cfg['cell_local_seconds_per_display_second']*display_time-self.star.redshift_factor*delay
  q=t/self.step;i=np.floor(q).astype('i4');f=q-i
  x=np.mod(np.arctan2(normals[:,1],normals[:,0]),2*np.pi)*self.cols/(2*np.pi)
  y=(np.arcsin(np.clip(normals[:,2],-1,1))+np.pi/2)*(self.rows-1)/np.pi
  ix=np.floor(x).astype('i4');iy=np.minimum(np.floor(y).astype('i4'),self.rows-2);fx=x-ix;fy=y-iy;jx=(ix+1)%self.cols
  out=np.empty(len(x));
  for key in np.unique(i):
   take=i==key;xx=ix[take];yy=iy[take];xx1=jx[take];a=fx[take];b=fy[take]
   def bilinear(image):return (1-a)*(1-b)*image[yy,xx]+a*(1-b)*image[yy,xx1]+(1-a)*b*image[yy+1,xx]+a*b*image[yy+1,xx1]
   out[take]=(1-f[take])*bilinear(self.atlas(int(key)))+f[take]*bilinear(self.atlas(int(key)+1))
  return out
