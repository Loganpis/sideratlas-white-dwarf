"""Eight-second comparisons, retaining B's original 32-second scan speed.

This does not export a final 32-second Reel. Each standalone preview has
only the three approved brand labels; comparison explanations live outside it.
"""
from pathlib import Path
import argparse,json,sys,time
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'src'))
from white_dwarf import ColourCache
from visualization import Renderer,Samples,orientation,linear_to_srgb
from mode_model import InteriorModes
from convective_response import ConvectiveSurface
from final_export import encoder,metadata


def research_samples(surface,cache):
    class ResearchSamples(Samples):
        def temperature(self,t,inc,az):
            camera=np.stack((self.a,self.b,self.c),axis=-1)
            normals=orientation(camera,inc,az)
            return surface.temperature(normals,t,self.delay)

        def radiance_y(self,temperature,cache_y):
            q=(temperature-cache.temperatures[0])/(cache.temperatures[1]-cache.temperatures[0])
            if np.any((q<0)|(q>len(cache.temperatures)-1)):
                raise ValueError('Model-centered atmosphere cache extrapolation')
            i=np.minimum(np.floor(q).astype('i4'),len(cache.temperatures)-2)
            f=q-i;j=self.j;u=self.fmu
            lo=cache_y[i,j]*(1-u)+cache_y[i,j+1]*u
            hi=cache_y[i+1,j]*(1-u)+cache_y[i+1,j+1]*u
            return lo*(1-f)+hi*f
    return ResearchSamples


def make_renderer(kind,cfg):
    if kind=='version-b':return Renderer(cfg)
    surface=InteriorModes() if kind=='interior-modes' else ConvectiveSurface()
    cache=ColourCache(ROOT/'data/research-colour-cache.npz')
    return Renderer(cfg,surface.star,cache,research_samples(surface,cache))


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('kind',choices=['version-b','interior-modes','convection-sensitivity'])
    parser.add_argument('--width',type=int,default=540)
    args=parser.parse_args()
    cfg=json.loads((ROOT/'config.json').read_text())
    cfg.update(width=args.width,height=round(args.width*16/9),fps=24,tile_rows=48)
    # Keep seconds=32 and physical_seconds=1721.6: the eight-second excerpt
    # uses the exact same physical and camera rate as approved version B.
    render=make_renderer(args.kind,cfg)
    out=ROOT/'preview'/f'{args.kind}-8s.mp4'
    process=encoder(out,cfg['width'],cfg['height'],cfg['fps'])
    count=8*cfg['fps'];start=time.monotonic()
    try:
        for k in range(count):
            frame=render.frame16(k)
            process.stdin.write(frame.astype('<u2',copy=False).tobytes())
            if k in [0,48,96,144]:
                Image.fromarray(np.uint8(frame/257+.5)).save(ROOT/'preview'/f'{args.kind}-{k:03}.png')
            if k%24==0:print(args.kind,k,'/',count,round(time.monotonic()-start,1),'s',flush=True)
        process.stdin.close()
        if process.wait():raise RuntimeError('Video encoder failed')
    except BaseException:
        process.kill();raise
    report=dict(kind=args.kind,frames=count,seconds=8,configuration=cfg,
                physical_duration_s=8*cfg['physical_seconds']/cfg['seconds'],
                temperature_bounds_K=render.temperature_bounds,linear_rgb_bounds=render.rgb_bounds,
                export=metadata(),render_elapsed_s=time.monotonic()-start)
    (ROOT/'preview'/f'{args.kind}-metadata.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Completed',out,flush=True)


if __name__=='__main__':main()
