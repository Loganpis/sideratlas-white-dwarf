"""Run the unmodified GYRE 9.1.1 eigenproblem on its supplied WDEC model.

No evolutionary track, mode driving, saturated amplitudes or observations are
fitted here. The input structure is kept byte-for-byte unchanged.
"""
from pathlib import Path
import argparse, hashlib, json, os, subprocess
import numpy as np

ROOT = Path(__file__).resolve().parent


def structure():
    path = ROOT/'data/wdec-evolved'
    lines = path.read_text().splitlines()
    n = int(lines[1].split()[0])
    values = [float(line[i:i+22])
              for line in lines[2:2+20*((n+3)//4)]
              for i in range(0, len(line), 22) if line[i:i+22].strip()]
    a = np.array(values).reshape(20, n)
    r, m, lum, temp, rho, pressure = a[:6]
    gamma1 = a[8]/(1-a[9]*a[15])
    ups_t = a[9]/a[8]
    gravity = 6.67259e-8*m/r**2
    n2 = gravity**2*rho/pressure*ups_t*(a[15]-a[14]+a[18])
    teff = (lum[-1]/(4*np.pi*r[-1]**2*5.670374419e-5))**.25
    info = dict(structure_source='GYRE v9.1.1 models/wdec/m0.593/evolved',
                input_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                points=n, mass_g=float(m[-1]), radius_cm=float(r[-1]),
                luminosity_erg_s=float(lum[-1]), teff_K=float(teff),
                logg_cgs=float(np.log10(gravity[-1])),
                equilibrium='WDEC relaxed model, MESA EOS and opacity flags enabled in supplied controlparams',
                composition='Supplied parameterized C/O core; He and H layers; not a new full evolutionary sequence',
                reference_G_cgs=6.67259e-8)
    (ROOT/'data/structure.json').write_text(json.dumps(info, indent=2)+'\n')
    np.savez_compressed(ROOT/'data/structure.npz', r_cm=r, m_g=m,
                        luminosity=lum, temperature=temp, rho=rho,
                        pressure=pressure, Gamma1=gamma1, N2=n2,
                        nabla=a[14], nabla_ad=a[15], Ledoux=a[18])
    return info


def namelist(weight, scheme, details, boundary='VACUUM', n_freq=1200):
    detail = ("detail_file_format = 'HDF'\n  detail_template = 'mode.%l.%n_pg.h5'\n"
              "  detail_item_list = 'l,n_pg,n_g,n_p,freq,E_norm,x,xi_r,xi_h,lag_P,lag_rho,lag_T,prop_type'\n") if details else ''
    return f"""&constants
 G_GRAVITY = 6.67259d-8
/
&model
 model_type = 'EVOL'
 file = '../../data/wdec-evolved'
 file_format = 'WDEC'
/
&mode
 l = 1
/
&mode
 l = 2
/
&osc
 outer_bound = '{boundary}'
 adiabatic = .true.
 nonadiabatic = .false.
 inertia_norm = 'BOTH'
/
&rot
/
&num
 diff_scheme = '{scheme}'
/
&scan
 grid_type = 'INVERSE'
 freq_min = 0.001
 freq_max = 0.005
 freq_min_units = 'HZ'
 freq_max_units = 'HZ'
 n_freq = {n_freq}
/
&grid
 w_osc = {weight}
 w_exp = {weight/5}
 w_ctr = {weight}
/
&ad_output
 summary_file = 'summary.h5'
 summary_item_list = 'id,l,n_pg,n_p,n_g,omega,freq,E_norm'
 freq_units = 'HZ'
 {detail}
/
&nad_output
/
"""


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--gyre', default='/private/tmp/sideratlas-wd-gyre/bin/gyre')
    parser.add_argument('--run', default='coarse')
    args = parser.parse_args()
    info = structure()
    options = {'coarse': (20, 'COLLOC_GL4'), 'fine': (40, 'COLLOC_GL6'),
               'finer': (80, 'COLLOC_GL6'), 'boundary': (80, 'COLLOC_GL6'),
               'scan': (80, 'COLLOC_GL6'), 'coarsened': (80,'COLLOC_GL6')}
    weight, scheme = options[args.run]
    run = ROOT/'calculations'/args.run
    run.mkdir(exist_ok=True)
    text = namelist(weight, scheme, args.run == 'fine',
        boundary='UNNO' if args.run=='boundary' else 'VACUUM',
        n_freq=2400 if args.run=='scan' else 1200)
    if args.run=='coarsened':
        lines=(ROOT/'data/wdec-evolved').read_text().splitlines()
        n=int(lines[1].split()[0])
        a=np.array([float(line[i:i+22]) for line in lines[2:2+20*((n+3)//4)]
            for i in range(0,len(line),22) if line[i:i+22].strip()]).reshape(20,n)
        a=a[:,::2]
        out=[lines[0],str(a.shape[1])]
        for row in a:
            out += [''.join(f'{v:22.15E}' for v in row[k:k+4]) for k in range(0,len(row),4)]
        (ROOT/'data/wdec-coarsened').write_text('\n'.join(out)+'\n')
        text=text.replace('wdec-evolved','wdec-coarsened')
    (run/'gyre.in').write_text(text)
    env = dict(os.environ, OMP_NUM_THREADS='2',
               GYRE_DIR=str(Path(args.gyre).resolve().parents[1]))
    with (run/'gyre.log').open('w') as log:
        subprocess.run([args.gyre, 'gyre.in'], cwd=run, env=env,
                       stdout=log, stderr=subprocess.STDOUT, check=True)
    print(json.dumps(info, indent=2))
    print('Completed', args.run, flush=True)


if __name__ == '__main__':
    main()
