"""Validate the one final film, global timing and color-managed compression."""
from pathlib import Path
import sys,json,subprocess,hashlib
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parent;BASE=ROOT.parent
sys.path.insert(0,str(BASE))
sys.path.insert(0,str(ROOT))
from final_export import DECODE_FILTER
from render_reel import input_fingerprint

def main():
    movie=ROOT/'output/sideratlas-no003-the-white-dwarf-32s.mp4'
    probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames',
        '-show_streams','-show_format','-of','json',str(movie)]))
    assert len(probe['streams'])==1;s=probe['streams'][0]
    assert s['codec_name']=='h264' and s['profile']=='High'
    assert (s['width'],s['height'],s['pix_fmt'])==(1080,1920,'yuv420p')
    assert s['avg_frame_rate']=='30/1' and int(s['nb_read_frames'])==960
    assert abs(float(probe['format']['duration'])-32)<1e-6
    assert all(s[k]=='bt709' for k in ['color_space','color_transfer','color_primaries']) and s['color_range']=='tv'
    subprocess.run(['ffmpeg','-v','error','-xerror','-i',str(movie),'-f','null','-'],check=True)
    stamps=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0',
        '-show_frames','-show_entries','frame=best_effort_timestamp_time','-of','json',str(movie)]))
    t=np.array([float(f['best_effort_timestamp_time']) for f in stamps['frames']]);assert len(t)==960
    assert np.max(abs(t-np.arange(960)/30))<1e-6
    fingerprint,_=input_fingerprint();meta=json.loads((ROOT/'output/render-metadata.json').read_text())
    assert fingerprint==meta['fingerprint']
    assert meta['max_padded_linear_Y_conservation_error']<1e-5
    assert meta['continuous_evolution'] and not meta['repeated_segments']
    checkpoints=meta['checkpoints'];assert [r['start'] for r in checkpoints]==list(range(0,960,120))
    assert all(r['frames']==120 and r['fingerprint']==fingerprint for r in checkpoints)
    # Decode selected production frames back through the inverse transfer,
    # comparing their pixels with source PNGs before quantization/encoding.
    indices=[0,240,480,720,959];errors=[]
    for k in indices:
        imagepath=ROOT/'validation'/f'decoded-{k:04}.png'
        subprocess.run(['ffmpeg','-v','error','-y','-i',str(movie),'-vf',
            f'select=eq(n\\,{k}),'+DECODE_FILTER,'-frames:v','1',str(imagepath)],check=True)
        decoded=np.asarray(Image.open(imagepath),dtype=float)/255
        original=np.asarray(Image.open(ROOT/'validation'/f'frame-{k:04}.png'),dtype=float)/255
        delta=decoded-original;mse=float(np.mean(delta*delta));psnr=float(-10*np.log10(mse))
        mae=float(np.mean(abs(delta)));assert psnr>35 and mae<.005
        errors.append(dict(frame=k,PSNR_dB=psnr,mean_absolute_sRGB_error=mae))
    # Verify adjacent frames at checkpoint joins, not repeated first frames.
    joins=[(k-1,k) for k in range(120,960,120)];select='+'.join(f'eq(n\\,{k})' for pair in joins for k in pair)
    raw=subprocess.check_output(['ffmpeg','-v','error','-i',str(movie),'-vf',
        'select='+select+','+DECODE_FILTER,'-fps_mode','passthrough','-f','rawvideo','-pix_fmt','rgb24','-'])
    frames=np.frombuffer(raw,dtype='u1').reshape(len(joins),2,1920,1080,3)
    diffs=[float(np.mean(abs(pair[1].astype(float)-pair[0]))/255) for pair in frames]
    assert max(diffs)<.025 and min(diffs)>0
    caption=(ROOT/'instagram-description.text').read_text();assert len(caption)<=2200
    report=dict(frames=960,duration_s=32,width=1080,height=1920,fps=30,
        codec=s['codec_name'],profile=s['profile'],pixel_format=s['pix_fmt'],color='Rec.709 limited',audio=False,
        full_decode_passed=True,timestamps_monotonic_and_uniform=True,max_PTS_error_s=float(np.max(abs(t-np.arange(960)/30))),
        source_fingerprint_verified=True,no_repeated_segments=True,checkpoint_joins_mean_sRGB_difference=diffs,
        color_managed_decode_checks=errors,caption_characters=len(caption),
        movie_bytes=movie.stat().st_size,sha256=hashlib.sha256(movie.read_bytes()).hexdigest())
    (ROOT/'validation/final-validation.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))

if __name__=='__main__':main()
