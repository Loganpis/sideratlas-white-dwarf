"""Robust lossless assembly, isolated from file-provider open timeouts.

All checkpoint bytes are verified before FFmpeg opens them. This remuxes the
existing encoded frames and never rerenders, repeats or recompresses them.
"""
from pathlib import Path
import json,hashlib,tempfile,subprocess,os
ROOT=Path(__file__).resolve().parent

def main():
    path=ROOT/'output/render-metadata.json';meta=json.loads(path.read_text())
    records=sorted(meta['checkpoints'],key=lambda r:r['start'])
    assert len(records)==8 and sum(r['frames'] for r in records)==960
    with tempfile.TemporaryDirectory(prefix='sideratlas-lossless-join-',dir='/private/tmp') as folder:
        temp=Path(folder);names=[]
        for r in records:
            name=f"{r['start']:04}-{r['stop']:04}.mp4"
            data=(ROOT/'output/.chunks'/name).read_bytes()
            assert hashlib.sha256(data).hexdigest()==r['sha256']
            (temp/name).write_bytes(data);names.append(name)
        (temp/'concat.txt').write_text(''.join(f"file '{name}'\n" for name in names))
        subprocess.run(['ffmpeg','-v','error','-xerror','-y','-f','concat','-safe','0',
            '-i',str(temp/'concat.txt'),'-map','0:v:0','-c','copy','-an','-movflags','+faststart',str(temp/'final.mp4')],check=True)
        probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(temp/'final.mp4')]))
        assert int(probe['streams'][0]['nb_read_frames'])==960
        assert abs(float(probe['format']['duration'])-32)<1e-6
        data=(temp/'final.mp4').read_bytes();destination=ROOT/'output/sideratlas-no003-the-white-dwarf-32s.mp4'
        candidate=destination.with_suffix('.assembling.mp4');candidate.write_bytes(data);os.replace(candidate,destination)
    meta['assembly']=dict(method='Verified byte-for-byte checkpoint copies in private temporary storage; FFmpeg concat with -xerror and stream copy',
        checkpoints_verified=8,frames_verified=960,duration_verified_s=32,reencoded=False,
        physical_calculations_or_rendered_frames_changed=False,sha256=hashlib.sha256(data).hexdigest())
    path.write_text(json.dumps(meta,indent=2)+'\n')
    print(json.dumps(meta['assembly'],indent=2),flush=True)

if __name__=='__main__':main()
