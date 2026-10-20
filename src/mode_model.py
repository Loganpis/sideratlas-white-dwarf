"""Interior-based mode clocks with explicitly prescribed surface excitation.

Adiabatic eigenfunctions do not predict an emergent flux amplitude. Surface
flux amplitudes, m assignments, phases and the set of excited modes below
are a declared illustrative excitation scenario, not GYRE predictions.
"""
from pathlib import Path
import json
import numpy as np
import h5py
from white_dwarf import Star, MODES, harmonic, DAAtmosphere, C, MSUN

ROOT = Path(__file__).resolve().parents[1]


class StructureStar(Star):
    def __init__(self):
        self.info = json.loads((ROOT/'data/structure.json').read_text())
        super().__init__(self.info['mass_g']/1000/MSUN, self.info['teff_K'])

    @property
    def radius_m(self):
        return self.info['radius_cm']/100

    @property
    def compactness(self):
        return 2*self.info['reference_G_cgs']*1e-3*self.mass_kg/(self.radius_m*C*C)

    @property
    def logg_cgs(self):
        return self.info['logg_cgs']


class InteriorModes:
    def __init__(self):
        self.star = StructureStar()
        with h5py.File(ROOT/'calculations/finer/summary.h5') as f:
            a = {k: f[k][...] for k in f}
        # Distinct g-mode eigenvalues, no surface rendering of radial nodes.
        selected = [(1,-4,0,.4), (1,-6,1,1.2), (1,-8,-1,2.1),
                    (2,-6,1,.7), (2,-8,2,1.8), (2,-10,-2,2.8)]
        # Match B's small-amplitude full-sphere/time temperature RMS in the
        # linear limit; equal variance per mode is an excitation assumption.
        old_mean_h2 = [1/3, 4/15, 1/3]
        old_variance = sum(m.local_bolometric_semiamplitude**2*h2/2
                           for m,h2 in zip(MODES, old_mean_h2))
        self.target_linear_temperature_rms = 12000/4*np.sqrt(old_variance)
        flux_variance = (4*self.target_linear_temperature_rms/self.star.temperature_k)**2
        self.modes = []
        for l,n,m,phase in selected:
            j = np.flatnonzero((a['l']==l)&(a['n_pg']==n))
            if len(j)!=1 or a['n_p'][j[0]]!=0:
                raise ValueError('Selected eigenvalue is not an isolated pure g mode')
            j = j[0]
            mean_h2 = 1/3 if l==1 else 4/15
            amplitude = np.sqrt(2*flux_variance/(len(selected)*mean_h2))
            # GYRE clocks are Newtonian local clocks; apply the constant
            # surface redshift once for the weak-field rendering.
            period = 1/float(a['freq']['re'][j])/self.star.redshift_factor
            self.modes.append(dict(l=l, n_pg=n, m=m, phase_rad=phase,
                                   period_infinity_s=period,
                                   period_GYRE_s=float(1/a['freq']['re'][j]),
                                   base_flux_amplitude=float(amplitude),
                                   normalized_inertia=float(a['E_norm'][j])))

    def flux(self, normals, time, delay=0.):
        value = np.zeros(np.shape(normals)[:-1], dtype=float)
        for mode in self.modes:
            value += mode['base_flux_amplitude']*harmonic(mode['l'],mode['m'],normals)*np.cos(
                2*np.pi*(time-delay)/mode['period_infinity_s']+mode['phase_rad'])
        return value

    def temperature(self, normals, time, delay=0.):
        return self.star.temperature_k*(1+self.flux(normals,time,delay))**.25


class ResearchAtmosphere(DAAtmosphere):
    def __init__(self):
        super().__init__()
        self.provenance = json.loads((ROOT/'data/research-spectra-provenance.json').read_text())
        self.spectra = {}
        import hashlib
        for record in self.provenance['records']:
            path = ROOT/record['file']
            if hashlib.sha256(path.read_bytes()).hexdigest()!=record['sha256']:
                raise ValueError('Modified atmosphere input')
            a = np.loadtxt(path)
            self.spectra[(record['teff_k'],record['logg_cgs'])] = (a[:,0]*.1,a[:,1]*.01)
        self.temperatures = np.array(sorted({k[0] for k in self.spectra}))
        self.gravities = np.array(sorted({k[1] for k in self.spectra}))


def build_atmosphere(step_nm=.25, output='research-colour-cache.npz'):
    star = StructureStar()
    atmosphere = ResearchAtmosphere()
    temp = np.linspace(star.temperature_k-160,star.temperature_k+160,65)
    mu = np.linspace(0,1,129)**2
    rgb,xyz = [],[]
    for t in temp:
        a,b = atmosphere.colour_radiance(t,star.logg_cgs,mu,star.redshift_factor,step_nm)
        rgb.append(a); xyz.append(b)
    np.savez_compressed(ROOT/'data'/output,temperature=temp,mu=mu,rgb=rgb,xyz=xyz,
                        metadata=json.dumps(dict(star=star.parameters(),
                        spectral_step_nm=step_nm,approximation='Quasi-static 1D DA flux + 3D broadband limb fits, as in B; recalculated at structural Teff/logg; not a new time-dependent atmosphere solution')))


if __name__=='__main__':
    model = InteriorModes()
    (ROOT/'data/selected-modes.json').write_text(json.dumps(dict(
        modes=model.modes, target_linear_temperature_rms_K=model.target_linear_temperature_rms,
        prescribed='Excited subset, equal surface-flux variance per mode, m assignments and phases; no growth-rate calculation or saturation model',
        rotation='None; m denotes a real standing-wave angular basis in a degenerate nonrotating spectrum'),indent=2)+'\n')
    build_atmosphere()
    print('Saved calculated mode selection and model-centered atmosphere cache',flush=True)
