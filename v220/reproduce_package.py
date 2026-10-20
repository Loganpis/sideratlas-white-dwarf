"""Check the released source tree in a separate fresh process and directory."""
from pathlib import Path
import subprocess,sys,json,hashlib,os,tempfile,zipfile
ROOT=Path(__file__).resolve().parent

def main():
    bundle=ROOT/'dist/sideratlas-white-dwarf-v2.2.0.zip'
    with tempfile.TemporaryDirectory(prefix='sideratlas-final-repro-') as tmp:
        with zipfile.ZipFile(bundle) as z:z.extractall(tmp)
        fresh=Path(tmp)/'sideratlas-white-dwarf'
        code='''from pathlib import Path
import sys,json,hashlib
import numpy as np
from PIL import Image
root=Path.cwd();sys.path.insert(0,str(root/'v220'));sys.path.insert(0,str(root/'v220/src'))
from final_renderer import FinalRenderer
from render_reel import input_fingerprint
cfg=json.loads((root/'v220/config.json').read_text());render=FinalRenderer(cfg)
frame=render.frame16(0);image=Image.fromarray(np.uint8(frame/257+.5))
path=root/'fresh-frame.png';image.save(path)
fingerprint,_=input_fingerprint()
print(json.dumps(dict(frame_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),source_fingerprint=fingerprint)))
'''
        env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1');env.pop('PYTHONPATH',None)
        result=subprocess.run([sys.executable,'-c',code],cwd=fresh,env=env,check=True,capture_output=True,text=True)
        data=json.loads(result.stdout.strip());expected=hashlib.sha256((ROOT/'validation/frame-0000.png').read_bytes()).hexdigest()
        original=json.loads((ROOT/'output/render-metadata.json').read_text())
        assert data['frame_sha256']==expected
        assert data['source_fingerprint']==original['fingerprint']
        report=dict(extracted_bundle_frame_zero_bit_identical=True,all_render_input_hashes_identical=True,
            source_fingerprint=data['source_fingerprint'],frame_zero_png_sha256=expected,
            python=sys.version,scope='Same installed dependencies and CPU architecture; no original workspace imports',
            numerical_outputs_reused=True)
    (ROOT/'validation/reproduction.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))

if __name__=='__main__':main()
