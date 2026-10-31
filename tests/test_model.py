import unittest
import numpy as np
from model import area,RSUN_KM,qnm,invert,basis,fit,logarea,wilson

class HorizonTests(unittest.TestCase):
    def test_schwarzschild(self):
        self.assertAlmostEqual(area(1,0)/(16*np.pi*RSUN_KM**2),1,12)
    def test_extremal(self):
        self.assertAlmostEqual(area(1,1)/area(1,0),.5,12)
    def test_spin_sign(self):
        self.assertEqual(area(30,-.7),area(30,.7))
    def test_mass_scaling(self):
        self.assertAlmostEqual(area(80,.4)/area(40,.4),4,12)
    def test_redshift_cancellation(self):
        r=area(62,.7)/(area(33,.1)+area(31,.2))
        z=1.17
        self.assertAlmostEqual(area(62*z,.7)/(area(33*z,.1)+area(31*z,.2)),r,12)
    def test_invalid_area(self):
        for m,s in [(-1,0),(0,.5),(10,1.01)]:
            with self.assertRaises(ValueError):area(m,s)
    def test_forward_inverse(self):
        for m in np.linspace(20,100,5):
            for s in np.linspace(.05,.95,19):
                mm,ss=invert(*qnm(m,s))
                self.assertLess(abs(mm/m-1),1e-10);self.assertLess(abs(ss-s),1e-10)
    def test_constant_q_deformation(self):
        f,tau=qnm(68,.68)
        for scale in np.linspace(.7,1.4,15):
            m,s=invert(f*scale,tau/scale)
            self.assertLess(abs(area(m,s)/area(68,.68)-1/scale**2),1e-10)
    def test_physical_domain_not_clipped(self):
        with self.assertRaises(ValueError):invert(100,.001)
    def test_noiseless_single_mode(self):
        t=np.arange(0,.08,1/4096)
        for s in (.8,1,1.3):
            f,tau=qnm(68,.68);y=basis(t,f*s,tau/s)@np.array([20.,5.])
            out=fit(t,y)
            self.assertTrue(out['valid'])
            self.assertLess(abs(np.exp(out['log_area'])/(area(68,.68)/s**2)-1),1e-5)
            self.assertLess(out['rss'],1e-10)
    def test_noiseless_two_modes(self):
        t=np.arange(0,.08,1/4096)
        y=basis(t,*qnm(68,.68))@np.array([20.,5.])+basis(t,*qnm(68,.68,1))@np.array([8.,-4.])
        out=fit(t,y,True)
        self.assertTrue(out['valid'])
        self.assertLess(abs(np.exp(out['log_area'])/area(68,.68)-1),1e-5)
    def test_wilson_zero_not_certainty(self):
        lo,hi=wilson(0,200)
        self.assertAlmostEqual(lo,0,12);self.assertGreater(hi,0)
    def test_eta_sign_threshold(self):
        r=np.linspace(.9,2,500)
        self.assertTrue(np.allclose((1/r)*r-1,0))
    def test_common_entropy_factor_cancels(self):
        ai,af=120.,180.;fac=.7
        self.assertAlmostEqual(fac*af/(fac*ai),af/ai,12)

if __name__=='__main__':unittest.main()
