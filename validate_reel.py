#!/usr/bin/env python3
"""Verify the finished movie and create its separate scientific guide."""
from pathlib import Path
import hashlib,json,os,shutil,subprocess,sys
ROOT=Path(__file__).resolve().parent
os.environ.setdefault('MPLCONFIGDIR',str(ROOT/'.cache/matplotlib'))
os.environ.setdefault('XDG_CACHE_HOME',str(ROOT/'.cache'))
sys.path.insert(0,str(ROOT/'src'))
import numpy as np
from PIL import Image
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager,colormaps
from visualization import configuration,FixedObserverPhotometry
from final_export import DECODE_FILTER


def main():
    out=ROOT/'output';validation=ROOT/'validation';assets=ROOT/'assets'
    validation.mkdir(exist_ok=True);assets.mkdir(exist_ok=True)
    cfg=configuration();movie=out/'sideratlas-no003-the-white-dwarf-32s.mp4'
    meta=json.loads((out/'render-metadata.json').read_text())
    probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(movie)]))
    assert len(probe['streams'])==1
    s=probe['streams'][0]
    for key,value in dict(codec_name='h264',profile='High',width=1080,height=1920,pix_fmt='yuv420p',
                          r_frame_rate='30/1',avg_frame_rate='30/1',nb_frames='960',
                          color_space='bt709',color_transfer='bt709',color_primaries='bt709',color_range='tv',
                          field_order='progressive').items():
        assert s.get(key)==value,(key,s.get(key),value)
    assert float(probe['format']['duration'])==32
    # All decoded frames must retain their exact constant-rate presentation times,
    # including the joins between independently encoded four-second chunks.
    timing=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_frames',
        '-show_entries','frame=best_effort_timestamp_time','-of','json',str(movie)]))
    times=np.array([float(f['best_effort_timestamp_time']) for f in timing['frames']])
    np.testing.assert_allclose(times,np.arange(960)/30,atol=6e-7,rtol=0)
    indices=sorted({int(f['frame']) for f in meta['stills']})
    select='+'.join(f'eq(n\\,{i})' for i in indices)
    raw=subprocess.check_output(['ffmpeg','-hide_banner','-loglevel','error','-i',str(movie),
        '-vf',f'select={select},'+DECODE_FILTER,'-fps_mode','vfr','-f','rawvideo','-pix_fmt','rgb24','-'])
    decoded=np.frombuffer(raw,np.uint8).reshape(len(indices),1920,1080,3)
    comparisons=[]
    for n,index in enumerate(indices):
        with np.load(out/f'frame-{index:04d}-rgb16.npz') as data:ref=data['rgb'].astype(float)/257
        error=decoded[n].astype(float)-ref
        mse=float(np.mean(error**2));psnr=float(10*np.log10(255**2/mse))
        assert psnr>44,psnr
        comparisons.append(dict(frame=index,srgb_PSNR_dB=psnr,absolute_99th_percentile_RGB_error=float(np.percentile(abs(error),99))))
    Image.fromarray(decoded[0]).save(assets/'cover.png')
    assert meta['labels']==['@sideratlas','NO.003','THE WHITE DWARF']
    assert meta['fixed_observer']=={'inclination_deg':55,'azimuth_deg':0}
    assert meta['physical_temperature_amplitude_gain']==1 and meta['clipping'] is False
    light=np.genfromtxt(out/'fixed-observer-light-curve.csv',delimiter=',',names=True)
    schedule=np.genfromtxt(out/'camera-schedule.csv',delimiter=',',names=True)
    assert len(light)==len(schedule)==960
    np.testing.assert_allclose(light['observer_time_s'],light['display_time_s']*53.8,atol=1e-12)
    np.testing.assert_allclose(light['display_time_s'],schedule['display_time_s'],atol=0)
    fixed=FixedObserverPhotometry(144,288,55,0);physical_shutter=1721.6/960;checks=[]
    for i in [0,119,120,239,240,479,480,719,720,959]:
        flux=fixed.flux(float(light['observer_time_s'][i]),physical_shutter,4)
        err=abs(flux-float(light['relative_CIE_Y_flux'][i]));assert err<2e-6
        checks.append(dict(frame=i,independent_fixed_observer_flux_error=err))
    create_guide(light,schedule,cfg,assets)
    report=dict(movie=dict(file=movie.name,bytes=movie.stat().st_size,
            sha256=hashlib.sha256(movie.read_bytes()).hexdigest(),width=1080,height=1920,fps=30,frames=960,seconds=32,
            codec='H.264 High',pixel_format='yuv420p',color='Rec.709 limited',progressive=True,audio=False),
        exact_frame_timing_including_chunk_joins=True,color_managed_source_frame_comparisons=comparisons,
        fixed_observer_checks=checks,only_approved_three_labels=True,
        fixed_observer_visible_flux_peak_to_peak_percent=float(np.ptp(light['relative_CIE_Y_flux'])*100),
        temperature_range_K=meta['temperature_range_K'],physical_amplitudes_unchanged=True,
        no_temperature_or_linear_RGB_clipping=True,
        numerical_convergence=json.loads((validation/'numerical-convergence.json').read_text()),
        caption_characters=len((ROOT/'instagram-description.text').read_text()))
    assert report['caption_characters']<=2200
    (validation/'final-validation.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))


def create_guide(light,schedule,cfg,assets):
    path=ROOT/'fonts/lmroman10-regular.otf';font_manager.fontManager.addfont(str(path))
    family=font_manager.FontProperties(fname=str(path)).get_name()
    plt.rcParams.update({'font.family':family,'mathtext.fontset':'cm','font.size':11})
    fig=plt.figure(figsize=(10,8),layout='constrained');gs=fig.add_gridspec(3,1,height_ratios=[3,1.4,.7])
    ax=fig.add_subplot(gs[0]);x=light['observer_time_s'];flux=100*(light['relative_CIE_Y_flux']-1)
    ax.plot(x,flux,color='#2c6588',lw=1.8)
    ax.set(xlabel='Observer time (s)',ylabel='Visible flux relative to equilibrium (%)',
           title='Physical light curve: fixed observer at i = 55°, az = 0°')
    ax.axhline(0,color='.6',lw=.5);ax.grid(alpha=.15)
    top=ax.secondary_xaxis('top',functions=(lambda v:v/53.8,lambda v:v*53.8));top.set_xlabel('Reel playback time (s)')
    ax=fig.add_subplot(gs[1]);ax.plot(schedule['display_time_s'],schedule['camera_inclination_deg'],label='Camera inclination')
    ax.plot(schedule['display_time_s'],schedule['camera_azimuth_deg'],label='Camera azimuth')
    ax.set(xlabel='Reel playback time (s)',ylabel='Angle (degrees)',title='Cinematic camera scan: independent of the fixed-observer curve')
    ax.legend(loc='center left',bbox_to_anchor=(1,0.5),fontsize=9);ax.grid(alpha=.15)
    ax=fig.add_subplot(gs[2]);t=np.linspace(-160,160,1024);u=.5*(1+np.arcsinh(t/18)/np.arcsinh(160/18))
    colors=colormaps['RdBu_r'].resampled(4097)(u)[:,:3]
    ax.imshow(colors[None],extent=(-160,160,0,1),aspect='auto')
    ax.set_yticks([]);ax.set_xticks([-160,-80,-40,0,40,80,160])
    ax.set_xlabel('Temperature departure from 12,000 K (K); fixed asinh contrast, not visible stellar color')
    fig.suptitle('SiderAtlas NO.003 — scientific guide\nThe film displays false color; this light curve uses physical DA atmosphere emission',fontsize=15)
    fig.savefig(assets/'scientific-guide.png',dpi=160);plt.close(fig)


if __name__=='__main__':main()
