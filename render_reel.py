#!/usr/bin/env python3
"""Render the approved minimalist 32-second SiderAtlas white-dwarf Reel."""
from pathlib import Path
from dataclasses import asdict
import argparse,csv,hashlib,json,subprocess,sys,time
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'src'))
import numpy as np
from PIL import Image
from visualization import Renderer,configuration,camera_direction,FixedObserverPhotometry
from white_dwarf import Star,MODES
from final_export import encoder,metadata


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--config',type=Path,default=ROOT/'config.json')
    p.add_argument('--output',type=Path,default=ROOT/'output')
    p.add_argument('--stills-only',action='store_true')
    p.add_argument('--frames',type=int,nargs='+',default=[0,240,480,720])
    args=p.parse_args();cfg=json.loads(args.config.read_text());out=args.output;out.mkdir(parents=True,exist_ok=True)
    started=time.monotonic();renderer=Renderer(cfg);count=cfg['fps']*cfg['seconds']
    def save_frame(i,rgb):
        name=f'frame-{i:04d}.png'
        Image.fromarray(np.uint8((rgb.astype('u4')+128)//257)).save(out/name)
        np.savez_compressed(out/f'frame-{i:04d}-rgb16.npz',rgb=rgb)
        return dict(frame=i,file=name,display_time_s=(i+.5)/cfg['fps'])
    if args.stills_only:
        for i in args.frames:
            rgb=renderer.frame16(i)
            save_frame(i,rgb)
        return
    source_files=[ROOT/'src/white_dwarf.py',ROOT/'src/visualization.py',ROOT/'data/colour-cache.npz',Path(__file__),ROOT/'final_export.py']
    source_hashes={str(f.relative_to(ROOT)):hashlib.sha256(f.read_bytes()).hexdigest() for f in source_files}
    fingerprint=hashlib.sha256(json.dumps(dict(configuration=cfg,source=source_hashes),sort_keys=True).encode()).hexdigest()
    parts=out/'.chunks';parts.mkdir(exist_ok=True);state_file=parts/'state.json'
    state=json.loads(state_file.read_text()) if state_file.exists() else dict(fingerprint=fingerprint,completed={},stills=[],temperature=[np.inf,-np.inf],rgb=[np.inf,-np.inf])
    if state['fingerprint']!=fingerprint:raise ValueError('Configuration/source changed; use a fresh output directory')
    size=4*cfg['fps']
    for begin in range(0,count,size):
        end=min(count,begin+size);name=f'chunk-{begin:06d}.mp4';path=parts/name
        if name in state['completed']:
            if hashlib.sha256(path.read_bytes()).hexdigest()!=state['completed'][name]:raise ValueError('Modified saved chunk')
            print(json.dumps(dict(resumed_chunk=name,through_frame=end-1)),flush=True);continue
        process=encoder(path,cfg['width'],cfg['height'],cfg['fps'])
        try:
            for i in range(begin,end):
                rgb=renderer.frame16(i)
                if i in args.frames:state['stills'].append(save_frame(i,rgb))
                process.stdin.write(rgb.astype('<u2',copy=False).tobytes())
                if i%cfg['fps']==0:print(json.dumps(dict(frame=i,frames=count,elapsed_s=time.monotonic()-started)),flush=True)
            process.stdin.close()
            if process.wait():raise RuntimeError('Encoding failed')
        except BaseException:
            process.kill();raise
        state['completed'][name]=hashlib.sha256(path.read_bytes()).hexdigest()
        for key,bounds in [('temperature',renderer.temperature_bounds),('rgb',renderer.rgb_bounds)]:
            state[key]=[min(state[key][0],bounds[0]),max(state[key][1],bounds[1])]
        temp=state_file.with_suffix('.tmp');temp.write_text(json.dumps(state,indent=2)+'\n');temp.replace(state_file)
        print(json.dumps(dict(completed_chunk=name,through_frame=end-1)),flush=True)
    listing=parts/'concat.txt'
    listing.write_text(''.join(f"file 'chunk-{i:06d}.mp4'\n" for i in range(0,count,size)))
    subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-f','concat','-safe','0','-i',str(listing),
        '-c','copy','-movflags','+faststart',str(out/'sideratlas-no003-the-white-dwarf-32s.mp4')],check=True)
    frames=state['stills']
    observer=cfg['fixed_observer']
    phot=FixedObserverPhotometry(inc=observer['inclination_deg'],az=observer['azimuth_deg'])
    shutter=cfg['physical_seconds']/count
    rows=[];schedule=[]
    for i in range(count):
        display=(i+.5)/cfg['fps'];physical=display*cfg['physical_seconds']/cfg['seconds']
        flux=phot.flux(physical,shutter,cfg['temporal_gauss_nodes'])
        rows.append([display,physical,flux])
        inc,az=camera_direction(display/cfg['seconds'],cfg)
        schedule.append([display,physical,float(inc),float(az)])
    for path,header,values in [
        (out/'fixed-observer-light-curve.csv',['display_time_s','observer_time_s','relative_CIE_Y_flux'],rows),
        (out/'camera-schedule.csv',['display_time_s','observer_time_s','camera_inclination_deg','camera_azimuth_deg'],schedule)]:
        with path.open('w',newline='') as f:
            w=csv.writer(f,lineterminator='\n');w.writerow(header);w.writerows(values)
    flux=np.array(rows)[:,2]
    report=dict(scope='Final continuous 32-second Reel; no forced loop or repeated 8-second clips',
        configuration=cfg,star=Star().parameters(),modes=[asdict(m) for m in MODES],
        physical_model='Original prescribed photospheric flux modes, not a solved interior eigenmode spectrum',
        labels=cfg['labels'],physical_temperature_amplitude_gain=1,
        temperature_range_K=state['temperature'],linear_falsecolor_rgb_range=state['rgb'],clipping=False,
        fixed_observer=cfg['fixed_observer'],camera_and_photometry='Fixed-observer curve is independent of cinematic camera direction',
        visible_flux_range=[float(flux.min()),float(flux.max())],visible_flux_peak_to_peak_percent=float(np.ptp(flux)*100),
        false_color='Fixed RdBu_r asinh scale +/-160K, softening 18K; palette RGB modulated by calculated time-dependent DA CIE Y radiance',
        observer_convention='n_obs=(-sin(i)cos(az),-sin(i)sin(az),cos(i)); fixed roll -20 degrees',
        camera='Smooth cinematic sequence of distant static viewing directions, not a material orbit or stellar rotation',
        temporal='Gauss-Legendre shutter mean of temperature and DA radiance; camera orientation evaluated at each shutter sample',
        display_speedup=cfg['physical_seconds']/cfg['seconds'],export=metadata(),stills=frames,
        resumable_export='Eight independently encoded four-second closed-GOP chunks concatenated without re-encoding; no repeated simulation frames',
        source_sha256={str(f.relative_to(ROOT)):hashlib.sha256(f.read_bytes()).hexdigest() for f in
            [ROOT/'config.json',ROOT/'src/white_dwarf.py',ROOT/'src/visualization.py',ROOT/'data/colour-cache.npz',Path(__file__),ROOT/'final_export.py']},
        elapsed_s=time.monotonic()-started)
    (out/'render-metadata.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(output=str(out),elapsed_s=report['elapsed_s'],temperature_range_K=report['temperature_range_K']),indent=2))


if __name__=='__main__':main()
