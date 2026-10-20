"""One continuous 32-second film, with resumable closed-GOP checkpoints."""
from pathlib import Path
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
os.environ.setdefault('OMP_NUM_THREADS','1')
import sys,json,time,hashlib,subprocess,multiprocessing,argparse
from concurrent.futures import ProcessPoolExecutor,as_completed
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parent;BASE=ROOT.parent
sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(BASE))
from final_renderer import FinalRenderer
from final_export import encoder,metadata

RENDER=None

def input_fingerprint():
    files=[BASE/'config.json',BASE/'render_previews.py',BASE/'final_export.py',
      BASE/'src/white_dwarf.py',BASE/'src/visualization.py',BASE/'src/mode_model.py',
      BASE/'luminous/src/luminous_render.py',ROOT/'src/final_renderer.py',ROOT/'src/surface_optics.py',ROOT/'config.json',Path(__file__),
      BASE/'calculations/finer/summary.h5']
    files += [p for p in (BASE/'data').iterdir() if p.is_file() and p.name!='convective-response.npz']
    files += list((BASE/'fonts').glob('*.otf'))
    files += [ROOT/'validation/surface-decision.json']
    hashes={str(p.relative_to(BASE)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(files)}
    return hashlib.sha256(json.dumps(hashes,sort_keys=True).encode()).hexdigest(),hashes

def initialize(config):
    global RENDER
    RENDER=FinalRenderer(config)

def atomic_json(path,data):
    temp=path.with_suffix(f'.{os.getpid()}.tmp');temp.write_text(json.dumps(data,indent=2)+'\n');temp.replace(path)

def render_chunk(start,stop,fingerprint):
    render=RENDER;cfg=render.cfg;folder=ROOT/'output/.chunks';stem=f'{start:04}-{stop:04}'
    target=folder/(stem+'.mp4');temp=folder/(stem+'.partial.mp4')
    render.temperature_bounds=[np.inf,-np.inf];render.optics.full_flux_error=[];render.optics.crop_fractions=[]
    p=encoder(temp,cfg['preview_width'],round(cfg['preview_width']*16/9),cfg['fps']);begin=time.monotonic()
    try:
        for k in range(start,stop):
            frame=render.frame16(k);p.stdin.write(frame.astype('<u2',copy=False).tobytes())
            if k in [0,240,480,720,959]:
                Image.fromarray(np.uint8(frame/257+.5)).save(ROOT/'validation'/f'frame-{k:04}.png')
            if (k-start+1)%30==0:
                atomic_json(folder/(stem+'.progress.json'),dict(start=start,stop=stop,completed=k-start+1,
                    fingerprint=fingerprint,elapsed_s=time.monotonic()-begin))
                print(f'Frames {start}..{k} complete ({time.monotonic()-begin:.1f} s)',flush=True)
        p.stdin.close()
        if p.wait():raise RuntimeError('Encoder failed')
    except BaseException:
        p.kill();raise
    temp.replace(target)
    report=dict(start=start,stop=stop,frames=stop-start,fingerprint=fingerprint,
        temperature_bounds_K=render.temperature_bounds,
        max_padded_linear_Y_conservation_error=max(render.optics.full_flux_error),
        cropped_Y_fraction_range=[min(render.optics.crop_fractions),max(render.optics.crop_fractions)],
        effective_Y_wavelength_nm=render.optics.effective_Y_wavelength_nm,
        repaired_limb_sliver_rays=render.repaired_limb_slivers,elapsed_s=time.monotonic()-begin,
        sha256=hashlib.sha256(target.read_bytes()).hexdigest())
    atomic_json(folder/(stem+'.json'),report)
    return report

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--workers',type=int);args=parser.parse_args()
    cfg=json.loads((ROOT/'config.json').read_text())
    decision=json.loads((ROOT/'validation/surface-decision.json').read_text())
    if cfg.get('granulation_enabled',False) or decision['visible_granulation_included']:
        raise RuntimeError('This production configuration excludes the rejected flow')
    if not decision['fallback_authorized']:
        raise RuntimeError('Scientific surface decision is missing')
    fingerprint,hashes=input_fingerprint()
    out=ROOT/'output';folder=out/'.chunks';folder.mkdir(exist_ok=True,parents=True)
    source=out/'input-fingerprint.json'
    if source.exists() and json.loads(source.read_text())['fingerprint']!=fingerprint:
        raise RuntimeError('Changed inputs: use a fresh checkpoint directory before rendering')
    atomic_json(source,dict(fingerprint=fingerprint,input_sha256=hashes))
    count=cfg['fps']*cfg['preview_seconds'];chunk=cfg['chunk_frames'];jobs=[];reports=[]
    for start in range(0,count,chunk):
        stop=min(start+chunk,count);stem=f'{start:04}-{stop:04}';rp=folder/(stem+'.json');video=folder/(stem+'.mp4')
        if rp.exists() and video.exists():
            r=json.loads(rp.read_text())
            if r['fingerprint']!=fingerprint or r['sha256']!=hashlib.sha256(video.read_bytes()).hexdigest():
                raise RuntimeError('Invalid checkpoint')
            reports.append(r)
        else:jobs.append((start,stop,fingerprint))
    begin=time.monotonic()
    if jobs:
        with ProcessPoolExecutor(max_workers=args.workers or cfg['render_workers'],
            mp_context=multiprocessing.get_context('spawn'),initializer=initialize,initargs=(cfg,)) as executor:
            futures=[executor.submit(render_chunk,*j) for j in jobs]
            for f in as_completed(futures):
                reports.append(f.result());print('Finished checkpoint',len(reports),'of',count//chunk,flush=True)
    report=dict(config=cfg,source_configuration=json.loads((BASE/'config.json').read_text()),
        fingerprint=fingerprint,frames=count,seconds=cfg['preview_seconds'],physical_seconds=1721.6,
        temperature_bounds_K=[min(r['temperature_bounds_K'][0] for r in reports),max(r['temperature_bounds_K'][1] for r in reports)],
        max_padded_linear_Y_conservation_error=max(r['max_padded_linear_Y_conservation_error'] for r in reports),
        cropped_Y_fraction_range=[min(r['cropped_Y_fraction_range'][0] for r in reports),max(r['cropped_Y_fraction_range'][1] for r in reports)],
        checkpoints=sorted(reports,key=lambda r:r['start']),export=metadata(),continuous_evolution=True,
        repeated_segments=False,seamless_loop_forcing=False,elapsed_this_run_s=time.monotonic()-begin)
    atomic_json(out/'render-metadata.json',report)
    from assemble_reel import main as assemble
    assemble()
    print('FINAL FILM COMPLETE',str(out/'sideratlas-no003-the-white-dwarf-32s.mp4'),flush=True)

if __name__=='__main__':main()
