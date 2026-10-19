from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import numpy as np
from numpy.polynomial.legendre import leggauss
from visualization import (configuration,camera_direction,orientation,Samples,Renderer,FixedObserverPhotometry,circle_rectangle_area)
from white_dwarf import Star,ray_map,flux_perturbation,temperature_from_flux,ColourCache,harmonic


def small_config():
    cfg=configuration();cfg.update(width=216,height=384,tile_rows=32,supersample=1,limb_supersample=4)
    return cfg


def test_view_rotations_and_analytic_harmonic_cancellation():
    x,w=leggauss(40);mu=(x+1)/2;weight=w/2*mu;phi=(np.arange(128)+.5)*2*np.pi/128
    nx=np.sqrt(1-mu[:,None]**2)*np.cos(phi);ny=np.sqrt(1-mu[:,None]**2)*np.sin(phi)
    camera=np.stack((nx,ny,np.broadcast_to(mu[:,None],nx.shape)),axis=-1)
    for inc,az in [(55,0),(55,-25),(70,25),(82,90)]:
        matrix=orientation(np.eye(3),inc,az)
        np.testing.assert_allclose(matrix@matrix.T,np.eye(3),atol=5e-16)
        np.testing.assert_allclose(np.linalg.det(matrix),1,atol=5e-16)
        n=orientation(camera,inc,az);observer=orientation(np.array([0.,0.,1.]),inc,az)
        for degree,order,factor in [(1,0,2/3),(1,1,2/3),(2,1,1/4)]:
            mean=np.sum(weight*harmonic(degree,order,n).mean(axis=1))/weight.sum()
            np.testing.assert_allclose(mean,factor*harmonic(degree,order,observer),atol=8e-15)


def test_optimized_retarded_field_and_y_interpolation_match_original():
    star=Star();grid=np.linspace(0,1,4097);cp,delay=ray_map(grid,star.compactness)
    rng=np.random.default_rng(27);x=rng.uniform(-.7,.7,500);y=rng.uniform(-.7,.7,500)
    sample=Samples(x,y,star,(grid,cp,delay));cache=ColourCache()
    camera=np.stack((sample.a,sample.b,sample.c),axis=-1)
    for t,inc,az in [(0,55,-25),(255.3,62.5,0),(1721.5,70,25)]:
        normals=orientation(camera,inc,az)
        original=temperature_from_flux(star,flux_perturbation(normals,t,sample.delay))
        np.testing.assert_allclose(sample.temperature(t,inc,az),original,atol=4e-12,rtol=0)
        direct=cache.intensity(original,sample.mu)[:,4]
        np.testing.assert_allclose(sample.radiance_y(original,cache.xyz[...,1]),direct,rtol=6e-16)


def test_fixed_observer_is_independent_of_cinematic_configuration():
    fixed=FixedObserverPhotometry(48,96)
    first=fixed.flux(255.3,1.7933333333)
    cfg=configuration();cfg['camera']['inclination_deg']=[0,90]
    cfg['camera']['azimuth_deg']=[-180,180]
    # The fixed-observer object has no dependency on the cinematic camera.
    assert fixed.flux(255.3,1.7933333333)==first
    other=FixedObserverPhotometry(48,96,inc=82.,az=90.)
    assert abs(other.flux(25.,1.7933333333)-fixed.flux(25.,1.7933333333))>1e-4


def test_only_approved_labels_and_black_background_outside_surface():
    cfg=small_config();renderer=Renderer(cfg);frame=renderer.frame16(0)
    assert frame.dtype==np.uint16 and frame.shape==(384,216,3)
    assert cfg['labels']==['@sideratlas','NO.003','THE WHITE DWARF']
    assert np.all(frame[:40]==0) and np.all(frame[-40:]==0)
    assert np.count_nonzero(renderer.text_alpha)>0
    assert np.max(renderer.text_alpha[int(.25*384):])==0
    assert renderer.temperature_bounds[0]>11800 and renderer.temperature_bounds[1]<12200
    assert 0<=renderer.rgb_bounds[0]<=renderer.rgb_bounds[1]<1


def test_cinematic_scan_and_fixed_scale_endpoints():
    cfg=configuration()
    np.testing.assert_allclose(camera_direction(0,cfg),(55,-25))
    np.testing.assert_allclose(camera_direction(1,cfg),(70,25))
    scale=cfg['temperature_scale_K'];soft=cfg['asinh_softening_K']
    t=np.array([-scale,0,scale])
    mapped=.5*(1+np.arcsinh(t/soft)/np.arcsinh(scale/soft))
    np.testing.assert_allclose(mapped,[0,.5,1])
    assert cfg['seconds']==32 and cfg['fps']==30
    assert cfg['physical_seconds']/cfg['seconds']==53.8


def test_exact_circle_coverage_known_areas_and_total_projected_disk():
    np.testing.assert_allclose(circle_rectangle_area(-1,1,-1,1,1),np.pi,atol=1e-14)
    np.testing.assert_allclose(circle_rectangle_area(0,1,0,1,1),np.pi/4,atol=1e-14)
    np.testing.assert_allclose(circle_rectangle_area(-.1,.1,-.1,.1,1),.04,atol=1e-14)
    np.testing.assert_allclose(circle_rectangle_area(2,3,2,3,1),0,atol=1e-14)
    cfg=small_config();renderer=Renderer(cfg);area=0.
    for tile in renderer.tiles:
        n=int(tile.regular.mask.sum());e=int(tile.edge_samples.mask.sum());f=int(tile.fallback_samples.mask.sum())
        projected=tile.project(np.ones((n,3)),np.ones((e,3)),np.ones((f,3)))
        area+=np.sum(projected[...,0],dtype='f8')
    radius=cfg['radius_fraction_of_width']*cfg['width']/renderer.star.redshift_factor
    np.testing.assert_allclose(area,np.pi*radius*radius,atol=2e-4,rtol=0)
