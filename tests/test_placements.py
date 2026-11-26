from dataclasses import replace
import numpy as np
from atlas_engine import GridConfig,PLACEMENTS,build_volume,placement_geometry_metrics,projection,overlay_metrics
from grid_model import spherical_shell_positions
from scientific_reference import ScientificCase


class PlacementTests(ScientificCase):
    def test_all_placements_bijective_on_rectangles_and_degenerate_grids(self):
        for placement in PLACEMENTS:
            for x in range(1,8):
                for y in range(1,8):
                    for start in [-3,10]:
                        c=GridConfig(x,y,3,'Multiples of k',3,placement,start,17)
                        n,s=build_volume(c)
                        with self.subTest(placement=placement,x=x,y=y,start=start):
                            self.assertEqual(n.size,len(set(n.ravel().tolist())))
                            self.assertEqual(sorted(n.ravel().tolist()),list(range(start,start+x*y*3)))
                            np.testing.assert_array_equal(s,n%3==0)

    def test_arithmetic_invariants_but_geometry_changes(self):
        cfg=GridConfig(7,6,4,start=10)
        reference=build_volume(cfg)
        changed=False
        m0=placement_geometry_metrics(cfg)
        for p in PLACEMENTS:
            c=replace(cfg,placement=p)
            n,s=build_volume(c)
            self.assertEqual(sorted(n[s].tolist()),sorted(reference[0][reference[1]].tolist()))
            m=placement_geometry_metrics(c)
            if p not in ('Linear','3D helix'):
                np.testing.assert_array_equal(np.diff(n,axis=0),42)
                self.assertAlmostEqual(m['alive_density'],m0['alive_density'])
                self.assertAlmostEqual(m['global_entropy'],m0['global_entropy'])
                changed |= abs(m['local_entropy_mean']-m0['local_entropy_mean'])>1e-6
            if p!='Linear':
                with self.assertRaises(ValueError): overlay_metrics(c)
        self.assertTrue(changed)

    def test_seeded_placement_and_weave_parameters(self):
        c=GridConfig(7,6,2,placement='Seeded random',placement_param=42)
        n,_=build_volume(c)
        other,_=build_volume(replace(c,placement_param=43))
        self.assertFalse(np.array_equal(n,other))
        c=replace(c,placement='Prime modulus weave',placement_param=7,start=10)
        n,_=build_volume(c)
        self.assertTrue(np.all(np.diff(n[0].ravel()%7)>=0))

    def test_spherical_formula_area_cells_poles_and_shell_rotation(self):
        X,Y,Z=9,7,4
        z,y,x=np.indices((Z,Y,X));x,y,z=x.ravel(),y.ravel(),z.ravel()
        pos=spherical_shell_positions(x,y,z,X,Y,5,2,30)
        h=1-2*(y+.5)/Y
        theta=2*np.pi*(x+.5)/X+np.pi*z/6
        radius=5+2*z
        expected=np.stack([radius*np.sqrt(1-h*h)*np.cos(theta),radius*np.sqrt(1-h*h)*np.sin(theta),radius*h],axis=1)
        np.testing.assert_allclose(pos,expected,rtol=1e-6,atol=1e-6)
        np.testing.assert_allclose(np.linalg.norm(pos,axis=1),radius,rtol=1e-6)
        self.assertTrue(np.all(abs(h)<1))
        self.assertEqual(np.unique(pos,axis=0).shape[0],X*Y*Z)
        heights=1-2*np.arange(Y+1)/Y
        np.testing.assert_allclose((2*np.pi/X)*(-np.diff(heights)),4*np.pi/(X*Y))

    def test_cartesian_coordinate_order(self):
        c=GridConfig(3,2,4,start=10)
        n,s=build_volume(c)
        z,y,x=np.nonzero(s)
        points=np.column_stack((x,y,z))
        for point,value in zip(points,n[s]):
            ix,iy,iz=point
            self.assertEqual(value,10+ix+3*iy+6*iz)
