#!/usr/bin/env python3
"""Assemble the source, inputs, final movie and measured validation bundle."""
from pathlib import Path
import hashlib,json,subprocess,zipfile
ROOT=Path(__file__).resolve().parent
VERSION='v1.0.0'


def main():
    dist=ROOT/'dist';dist.mkdir(exist_ok=True)
    files=[]
    for name in ['README.md','LICENSE','.gitignore','config.json','requirements.txt','requirements-lock.txt','instagram-description.text']:
        files.append(ROOT/name)
    for pattern in ['*.py','src/*.py','tests/*.py','docs/*.md','data/*','fonts/*','assets/*.png',
                    'output/*.mp4','output/*.png','output/*.npz','output/*.csv','output/*.json',
                    'validation/numerical-convergence.json','validation/final-validation.json','validation/tests.txt','validation/runtime-environment.json']:
        files.extend(p for p in ROOT.glob(pattern) if p.is_file())
    files=sorted(set(files))
    assert (ROOT/'validation/final-validation.json') in files
    assert (ROOT/'output/sideratlas-no003-the-white-dwarf-32s.mp4') in files
    commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    manifest=dict(version=VERSION,git_commit=commit,
        files=[dict(path=str(p.relative_to(ROOT)),bytes=p.stat().st_size,
                    sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in files])
    bundle=dist/f'sideratlas-white-dwarf-{VERSION}.zip'
    with zipfile.ZipFile(bundle,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as archive:
        for p in files:
            kind=zipfile.ZIP_STORED if p.suffix in ['.mp4','.npz','.png'] else zipfile.ZIP_DEFLATED
            archive.write(p,arcname=str(p.relative_to(ROOT)),compress_type=kind)
        archive.writestr('PACKAGE-MANIFEST.json',json.dumps(manifest,indent=2)+'\n')
    check_files=[ROOT/'output/sideratlas-no003-the-white-dwarf-32s.mp4',ROOT/'instagram-description.text',bundle]
    (dist/'SHA256SUMS.txt').write_text(''.join(f'{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.name}\n' for p in check_files))
    with zipfile.ZipFile(bundle) as archive:
        assert archive.testzip() is None
        for record in manifest['files']:
            assert hashlib.sha256(archive.read(record['path'])).hexdigest()==record['sha256']
    print(json.dumps(dict(bundle=str(bundle),bytes=bundle.stat().st_size,files=len(files),git_commit=commit),indent=2))


if __name__=='__main__':main()
