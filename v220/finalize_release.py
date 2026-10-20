"""Finish the current local render, validation and packaging; never publishes."""
from pathlib import Path
import subprocess,sys,time,json
ROOT=Path(__file__).resolve().parent

def status(stage,**extra):
    (ROOT/'calculations').mkdir(exist_ok=True)
    (ROOT/'calculations/finalization.json').write_text(json.dumps(dict(stage=stage,**extra),indent=2)+'\n')
    print(stage,flush=True)

def main():
    try:
        status('Waiting for the active full render')
        deadline=time.monotonic()+7200
        while True:
            metadata=ROOT/'output/render-metadata.json'
            try:
                ready=metadata.exists() and bool(json.loads(metadata.read_text()).get('assembly')) and (ROOT/'output/sideratlas-no003-the-white-dwarf-32s.mp4').exists()
            except (ValueError,OSError):ready=False
            if ready:break
            log=(ROOT/'calculations/render.log').read_text()
            if 'Traceback (most recent last)' in log or 'Traceback (most recent call last)' in log:raise RuntimeError('Render reported a failure')
            if time.monotonic()>deadline:raise TimeoutError('Waiting for the renderer exceeded two hours')
            time.sleep(15)
        for stage,script in [('Validating final media','validate_reel.py'),
            ('Building the single-film package','package_release.py'),
            ('Reproducing a frame from a fresh extraction','reproduce_package.py'),
            ('Packaging the verified reproduction report','package_release.py')]:
            status(stage);subprocess.run([sys.executable,str(ROOT/script)],cwd=ROOT,check=True)
        status('Complete',movie=str(ROOT/'output/sideratlas-no003-the-white-dwarf-32s.mp4'),
            archive=str(ROOT/'dist/sideratlas-white-dwarf-v2.2.0.zip'))
    except BaseException as exc:
        status('Failed',error=repr(exc));raise

if __name__=='__main__':main()
