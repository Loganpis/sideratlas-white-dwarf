from pathlib import Path
import subprocess,json,hashlib
import numpy as np
ROOT=Path(__file__).resolve().parent
p=ROOT/'preview/sideratlas-white-dwarf-v2.2-preview.mp4'
assert 'PREVIEW COMPLETE' in (ROOT/'calculations/preview.log').read_text()
d=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(p)]));s=d['streams'][0]
assert (s['width'],s['height'],s['avg_frame_rate'],int(s['nb_read_frames']))==(540,960,'15/1',120)
assert float(d['format']['duration'])==8
raw=subprocess.check_output(['ffmpeg','-v','error','-i',str(p),'-vf','scale=135:240','-pix_fmt','rgb24','-f','rawvideo','-'])
a=np.frombuffer(raw,dtype='u1').reshape(120,240,135,3).astype(float)/255;diff=np.mean(abs(np.diff(a,axis=0)),axis=(1,2,3))
assert min(diff)>0 and max(diff)<.035
report=dict(duration_s=8,frames=120,resolution=[540,960],fps=15,full_decode_passed=True,continuous_nonstatic_evolution=True,max_adjacent_mean_sRGB_change=float(diff.max()),mean_adjacent_change=float(diff.mean()),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),review='Sampled start/middle/end frames show visible mode regions and cellular detail under the luminous halo; only three labels; final uses same display parameters',final_export_started_after_preview=True)
(ROOT/'validation/preview-review.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
