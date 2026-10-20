"""Optional Montgomery (2005) nonlinear envelope-response sensitivity study.

This is NOT a nonadiabatic eigenmode/driving or saturation calculation.
tau0=100 s and N=90 are prescribed representative response parameters.
The published equation has F_phot = F_base + tau_C dF_phot/dt. We compute
its bounded forced solution by backward integration, discarding a future
terminal layer. This is a forced boundary-value response, not forward
hydrodynamical evolution or a stability calculation.
"""
from pathlib import Path
import json
import numpy as np
from scipy.interpolate import RegularGridInterpolator
from mode_model import InteriorModes
from white_dwarf import harmonic

ROOT = Path(__file__).resolve().parents[1]


def solve(normals, duration=430.4, dt=.5, padding=10000., tau0=100., exponent=90., storage='f4'):
    model = InteriorModes()
    normals = np.asarray(normals)
    shape = normals.shape[:-1]
    h = np.stack([m['base_flux_amplitude']*harmonic(m['l'],m['m'],normals).ravel()
                  for m in model.modes])
    omega = np.array([2*np.pi/m['period_infinity_s'] for m in model.modes])
    phase = np.array([m['phase_rad'] for m in model.modes])
    count = int(np.ceil(duration/dt))
    steps = count+int(np.ceil(padding/dt))
    tau = tau0/model.star.redshift_factor
    # Analytic forcing is sampled at every RK stage, not interpolated.
    times = np.arange(2*steps+1)*dt/2
    c = np.cos(times[:,None]*omega+phase)
    y = np.ones(h.shape[1])
    output = np.empty((count+1,h.shape[1]),dtype=storage)
    def rhs(y,b):
        if np.any(y<=0):raise ValueError('Nonpositive emergent flux')
        return (y-b)*y**(exponent/4)/tau
    for k in range(steps,0,-1):
        base0 = 1+c[2*k]@h
        basem = 1+c[2*k-1]@h
        base1 = 1+c[2*k-2]@h
        k1 = rhs(y,base0)
        k2 = rhs(y-dt*k1/2,basem)
        k3 = rhs(y-dt*k2/2,basem)
        k4 = rhs(y-dt*k3,base1)
        y = y-dt*(k1+2*k2+2*k3+k4)/6
        if k-1<=count:output[k-1]=y
    return np.arange(count+1)*dt,output.reshape((count+1,)+shape)


def build_grid():
    theta = np.linspace(0,np.pi,97)
    phi = np.linspace(0,2*np.pi,193)
    th,ph = np.meshgrid(theta,phi,indexing='ij')
    normals = np.stack((np.sin(th)*np.cos(ph),np.sin(th)*np.sin(ph),np.cos(th)),axis=-1)
    time,flux = solve(normals,duration=432.)
    np.savez_compressed(ROOT/'data/convective-response.npz',time=time,theta=theta,
                        phi=phi,flux=flux,metadata=json.dumps(dict(
        tau0_proper_s=100,temperature_exponent=90,dt_infinity_s=.5,
        future_padding_s=10000,method='RK4 bounded forced solution; backwards integration of Montgomery 2005 Eq 2',
        status='Sensitivity study; parameters prescribed, not calibrated to this WDEC structure or a measured star',
        source='https://arxiv.org/abs/astro-ph/0507444')))
    print('Saved convective sensitivity grid',flux.shape,flush=True)


class ConvectiveSurface:
    def __init__(self):
        self.model = InteriorModes()
        self.star = self.model.star
        with np.load(ROOT/'data/convective-response.npz') as f:
            self.time = f['time'];self.theta=f['theta'];self.phi=f['phi']
            self.flux = f['flux']
        self.interpolator = RegularGridInterpolator((self.time,self.theta,self.phi),self.flux,
                                                    bounds_error=True)

    def temperature(self,normals,time,delay=0.):
        shape = np.shape(normals)[:-1]
        theta = np.arccos(np.clip(normals[...,2],-1,1))
        phi = np.mod(np.arctan2(normals[...,1],normals[...,0]),2*np.pi)
        t = np.broadcast_to(np.asarray(time)-delay,shape)
        # Queries stay inside the stored interval; no time wrap/reset.
        f = self.interpolator(np.stack((t,theta,phi),axis=-1))
        return self.star.temperature_k*f**.25


if __name__=='__main__':
    build_grid()
