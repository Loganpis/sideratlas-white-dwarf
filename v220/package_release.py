"""Create one portable release tree; retain inputs, omit all earlier movies."""
from pathlib import Path
import json,hashlib,zipfile,argparse,shutil
ROOT=Path(__file__).resolve().parent;BASE=ROOT.parent

def selected_files():
    files=[]
    for folder in ['data','fonts','licenses','calculations']:
        files += [p for p in (BASE/folder).rglob('*') if p.is_file() and p.suffix not in ['.log','.pyc']
                  and p.name!='convective-response.npz' and '__pycache__' not in p.parts]
    for name in ['white_dwarf.py','visualization.py','mode_model.py','convective_response.py']:
        files.append(BASE/'src'/name)
    for name in ['config.json','LICENSE','requirements-lock.txt','requirements-research.txt',
                 'render_previews.py','final_export.py','validate_research.py','calculate_modes.py','summarize_mode_convergence.py']:
        files.append(BASE/name)
    for name in ['mode-convergence.json','surface-validation.json','gyre-regression.txt','runtime-environment.json']:
        files.append(BASE/'validation'/name)
    lum=BASE/'luminous'
    for name in ['src/luminous_render.py','config.json','analyze_coupling.py','investigate_nonadiabatic.py','validate_optics.py',
                 'validation/optics-validation.json','validation/coupling-audit.json','data/wdec-static-gsm.h5']:
        files.append(lum/name)
    files += [p for p in (lum/'calculations').rglob('*') if p.is_file() and p.suffix not in ['.log','.pyc']]
    for dirname in ['src','data','docs','validation','output']:
        files += [p for p in (ROOT/dirname).rglob('*') if p.is_file() and '__pycache__' not in p.parts
                  and '.chunks' not in p.parts and not p.name.startswith(('decoded-','native-check-','check-')) and p.suffix not in ['.pyc','.log'] and p.name!='render-benchmark.json']
    files += [p for p in ROOT.iterdir() if p.is_file() and p.suffix in ['.py','.json','.text','.md'] and p.name not in ['benchmark_render.py','README.md']]
    return sorted(set(files))

def stage():
    target=ROOT/'staging/sideratlas-white-dwarf';target.mkdir(parents=True,exist_ok=True)
    payload={str(p.relative_to(BASE)):p.read_bytes() for p in selected_files()}
    # Root documentation points straight to the current single-film pipeline.
    readme=(ROOT/'README.md').read_text()
    payload['README.md']=readme.encode()
    payload['requirements-lock.txt']=((BASE/'requirements-lock.txt').read_text()+'h5py==3.11.0\nnumba==0.59.1\nllvmlite==0.42.0\n').encode()
    payload['instagram-description.text']=(ROOT/'instagram-description.text').read_bytes()
    payload['DATA-CREDITS.md']=(ROOT/'docs/DATA-CREDITS.md').read_bytes()
    payload['assets/cover.png']=(ROOT/'validation/frame-0480.png').read_bytes()
    license_path=BASE/'licenses/WDEC-LICENSE.txt'
    if not license_path.exists():license_path=BASE/'third_party/wdec/LICENSE.txt'
    payload['licenses/WDEC-LICENSE.txt']=license_path.read_bytes()
    payload['.gitignore']=b'.DS_Store\n__pycache__/\n*.pyc\n.cache/\n.venv/\n*.log\n*.mp4\n*.zip\n**/.chunks/\n**/staging/\n**/dist/\n'
    for name,data in payload.items():
        dest=target/name;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
    expected={target/name for name in payload}
    # This is a generated staging tree only, not the user's working repository.
    for p in target.rglob('*'):
        if p.is_file() and p not in expected and p.name!='MANIFEST.json':p.unlink()
    manifest=dict(version='2.2.0',date='2026-10-20',scope='One final six-mode Reel with enhanced pulsations, magnified statistical cellular convection and luminous imaging',
        files=[dict(path=k,bytes=len(v),sha256=hashlib.sha256(v).hexdigest()) for k,v in sorted(payload.items())])
    (target/'MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
    return target,manifest

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--stage-only',action='store_true');args=parser.parse_args()
    target,manifest=stage()
    if args.stage_only:print(target);return
    dist=ROOT/'dist';dist.mkdir(exist_ok=True)
    archive=dist/'sideratlas-white-dwarf-v2.2.0.zip';prefix='sideratlas-white-dwarf/'
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for p in sorted(target.rglob('*')):
            if p.is_file():z.write(p,prefix+str(p.relative_to(target)))
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        videos=[name for name in z.namelist() if name.endswith('.mp4')];assert len(videos)==1
        for f in manifest['files']:
            assert hashlib.sha256(z.read(prefix+f['path'])).hexdigest()==f['sha256']
    digest=hashlib.sha256(archive.read_bytes()).hexdigest()
    (dist/'SHA256SUMS.txt').write_text(f'{digest}  {archive.name}\n')
    print(json.dumps(dict(archive=str(archive),bytes=archive.stat().st_size,files=len(manifest['files']),
        sha256=digest,only_one_video=True),indent=2))

if __name__=='__main__':main()
