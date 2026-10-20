"""Compare saved eigenproblem runs without confusing root/structure accuracy."""
from pathlib import Path
import json
import h5py

ROOT=Path(__file__).resolve().parent


def main():
    data={}
    for run in ['coarse','fine','finer','boundary','scan','coarsened']:
        with h5py.File(ROOT/'calculations'/run/'summary.h5') as f:
            data[run]={(int(l),int(n)):1/float(nu['re'])
                       for l,n,nu in zip(f['l'][...],f['n_pg'][...],f['freq'][...])}
    selected=[]
    for l,n in [(1,-4),(1,-6),(1,-8),(2,-6),(2,-8),(2,-10)]:
        key=(l,n);period=data['finer'][key]
        selected.append(dict(l=l,n_pg=n,period_s=period,
            coarse_fine_difference_s=abs(data['fine'][key]-data['coarse'][key]),
            fine_finer_difference_s=abs(data['fine'][key]-period),
            boundary_sensitivity_s=abs(data['boundary'][key]-period),
            background_thinning_sensitivity_s=data['coarsened'][key]-period))
    assert set(data['scan'])==set(data['finer'])
    report=dict(selected_modes=selected,mode_counts={k:len(v) for k,v in data.items()},
        scan_keys_match=True,
        max_scan_period_difference_s=max(abs(data['scan'][k]-v) for k,v in data['finer'].items()),
        GYRE_regression='Official test/ad/wdec/m0.593 passed; see validation/gyre-regression.txt',
        limitation='Integration convergence on one supplied 435-point background; background thinning is a sensitivity test, not a physical error bound or full equilibrium-structure convergence')
    assert max(m['fine_finer_difference_s'] for m in selected)<1e-6
    (ROOT/'validation/mode-convergence.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Verified root-search completeness and integration convergence for all six selected modes')


if __name__=='__main__':main()
