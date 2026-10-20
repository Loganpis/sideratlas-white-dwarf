"""Bounded frozen-convection diagnostic; never imported by the renderer.

Agreement of a numerical root is not validation of DAV convective driving.
The two closures deliberately probe the limits of the retained WDEC model.
"""
from pathlib import Path
import os,sys,subprocess,argparse,json
import numpy as np
import h5py

ROOT=Path(__file__).resolve().parent
PARENT=ROOT.parent


def gsm_conversion():
    # GYRE's WDEC reader does not define c_egv. GSM 1.10 explicitly sets
    # this coefficient to zero, freezing background cooling on a mode cycle.
    # This is a stated extra assumption for this diagnostic, not a source patch.
    lines=(PARENT/'data/wdec-evolved').read_text().splitlines()
    n=int(lines[1].split()[0])
    a=np.array([float(line[i:i+22]) for line in lines[2:2+20*((n+3)//4)]
                for i in range(0,len(line),22) if line[i:i+22].strip()]).reshape(20,n)
    r,m,L,T,rho,P=a[:6];gravity=6.67259e-8*m/r**2
    gamma1=a[8]/(1-a[9]*a[15]);delta=a[9]/a[8]
    n2=gravity**2*rho/P*delta*(a[15]-a[14]+a[18])
    data=dict(r=r,M_r=m,L_r=L,P=P,rho=rho,T=T,N2=n2,Gamma_1=gamma1,
        nabla_ad=a[15],delta=delta,nabla=a[14],kap=a[17],
        kap_kap_rho=a[17]*a[12],kap_kap_T=a[17]*a[13],eps=a[6],
        eps_eps_rho=a[6]*a[11],eps_eps_T=a[6]*a[10],Omega_rot=np.zeros(n))
    path=ROOT/'data/wdec-static-gsm.h5'
    with h5py.File(path,'w') as f:
        for k,v in dict(version=110,n=n).items():f.attrs[k]=np.int32(v)
        for k,v in dict(M_star=m[-1],R_star=r[-1],L_star=L[-1]).items():f.attrs[k]=np.float64(v)
        for k,v in data.items():f.create_dataset(k,data=np.asarray(v,dtype='<f8'))
    return path


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('closure',choices=['1','4'])
    parser.add_argument('--gyre',default='/private/tmp/sideratlas-wd-gyre/bin/gyre')
    parser.add_argument('--fine',action='store_true')
    args=parser.parse_args()
    gsm_conversion()
    suffix='-fine' if args.fine else ''
    run=ROOT/'calculations'/('gsm-frozen-'+args.closure+suffix);run.mkdir(exist_ok=True)
    # Narrower radial-order set containing the six retained modes.
    text=f"""&constants
 G_GRAVITY = 6.67259d-8
/
&model
 model_type = 'EVOL'
 file = '../../data/wdec-static-gsm.h5'
 file_format = 'GSM'
/
&mode
 l = 1
 n_pg_min = -8
 n_pg_max = -4
/
&mode
 l = 2
 n_pg_min = -10
 n_pg_max = -6
/
&osc
 outer_bound = 'VACUUM'
 nonadiabatic = .true.
 conv_scheme = 'FROZEN_PESNELL_{args.closure}'
/
&rot
/
&num
 diff_scheme = '{'COLLOC_GL6' if args.fine else 'COLLOC_GL4'}'
/
&scan
 grid_type = 'INVERSE'
 freq_min = 0.002
 freq_max = 0.0045
 freq_min_units = 'HZ'
 freq_max_units = 'HZ'
 n_freq = 600
/
&grid
 w_osc = {80 if args.fine else 40}
 w_exp = {16 if args.fine else 8}
 w_ctr = {80 if args.fine else 40}
/
&ad_output
 summary_file = 'adiabatic.h5'
 summary_item_list = 'id,l,n_pg,omega,freq'
 freq_units = 'HZ'
/
&nad_output
 summary_file = 'nonadiabatic.h5'
 summary_item_list = 'id,l,n_pg,n_p,n_g,omega,freq,E_norm,eta'
 freq_units = 'HZ'
 detail_template = 'mode.%l.%n_pg.h5'
 detail_item_list = 'l,n_pg,freq,x,xi_r,xi_h,lag_T,lag_L,lag_S'
/
"""
    (run/'gyre.in').write_text(text)
    env=dict(os.environ,OMP_NUM_THREADS='2',GYRE_DIR=str(Path(args.gyre).resolve().parents[1]))
    status={'closure':args.closure,'used_in_preview':False,
            'extra_assumption':'Background cooling coefficient c_egv=0, as specified by GSM 1.10'}
    with (run/'gyre.log').open('w') as log:
        try:
            result=subprocess.run([args.gyre,'gyre.in'],cwd=run,env=env,stdout=log,
                                  stderr=subprocess.STDOUT,timeout=240)
            status['returncode']=result.returncode
        except subprocess.TimeoutExpired:
            status['timeout_s']=240
    (run/'status.json').write_text(json.dumps(status,indent=2)+'\n')
    print(status,flush=True)


if __name__=='__main__':main()
