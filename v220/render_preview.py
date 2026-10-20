from pathlib import Path
import os
os.environ['OPENBLAS_NUM_THREADS']='1';os.environ['OMP_NUM_THREADS']='1'
import sys,json,time,argparse
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parent;sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT.parent))
from final_renderer import FinalRenderer
from final_export import encoder
p=argparse.ArgumentParser();p.add_argument('--still',action='store_true');args=p.parse_args()
cfg=json.loads((ROOT/'config.json').read_text());cfg.update(preview_width=540,fps=15)
r=FinalRenderer(cfg);folder=ROOT/'preview';folder.mkdir(exist_ok=True);begin=time.time()
if args.still:
 frame=r.frame16(12);Image.fromarray(np.uint8(frame/257+.5)).save(folder/'preview-still.png');print('STILL',time.time()-begin,flush=True)
else:
 proc=encoder(folder/'sideratlas-white-dwarf-v2.2-preview.mp4',540,960,15)
 for k in range(120):
  f=r.frame16(k);proc.stdin.write(f.astype('<u2').tobytes())
  if k in [0,30,60,90,119]:Image.fromarray(np.uint8(f/257+.5)).save(folder/f'frame-{k:03}.png')
  if k%15==0:print(k,time.time()-begin,flush=True)
 proc.stdin.close();assert proc.wait()==0
 print('PREVIEW COMPLETE',time.time()-begin,flush=True)
