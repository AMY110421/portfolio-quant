"""Numerical invariants and regression checks, using only unittest and NumPy."""
import importlib.util
from pathlib import Path
import sys
import unittest
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'black_scholes_fd'))
sys.path.insert(0,str(ROOT/'equations_stochastiques'))
sys.path.insert(0,str(ROOT/'confidentialite_differentielle'))
from pricing import Market, black_scholes_call, finite_difference_call, _solve_tridiagonal
from simulation import brownian, euler_eds, gbm_convergence
from mechanisms import laplace_mechanism, gaussian_scale, gaussian_mechanism_from_eps_delta
from utils import compute_sensitivity, compute_stats, adjacent_replacement
from verification import distribution_diagnostic


class PricingTests(unittest.TestCase):
    def test_reference_and_no_arbitrage(self):
        m=Market()
        self.assertAlmostEqual(black_scholes_call(m),10.450583572185565,places=10)
        for scheme in ['explicit','implicit']:
            price=finite_difference_call(m,scheme=scheme)
            self.assertLess(abs(price-black_scholes_call(m)),.012)
            self.assertGreaterEqual(price,max(0,m.spot-m.strike*np.exp(-m.rate*m.maturity)))
            self.assertLessEqual(price,m.spot)

    def test_refinement_reduces_error(self):
        m=Market();exact=black_scholes_call(m)
        for scheme in ['explicit','implicit']:
            coarse=finite_difference_call(m,scheme=scheme,space_steps=100,time_steps=2000)
            fine=finite_difference_call(m,scheme=scheme,space_steps=200,time_steps=2000)
            self.assertLess(abs(fine-exact),abs(coarse-exact))

    def test_reject_bad_grid_and_parameters(self):
        for kwargs in [{'time_steps':1},{'space_steps':2},{'s_max':100},{'s_max':float('nan')},{'space_steps':10.5}]:
            with self.assertRaises(ValueError):finite_difference_call(Market(),scheme='explicit',**kwargs)
        with self.assertRaises(ValueError):black_scholes_call(Market(spot=float('nan')))
        with self.assertRaises(ValueError):finite_difference_call(Market(rate=.2,volatility=.1),scheme='implicit')

    def test_tridiagonal_residual(self):
        n=12;rng=np.random.default_rng(8)
        lower=np.full(n,-1.);upper=np.full(n,-1.);diag=np.full(n,4.);rhs=rng.normal(size=n)
        matrix=np.diag(diag)+np.diag(lower[1:],-1)+np.diag(upper[:-1],1)
        np.testing.assert_allclose(matrix@_solve_tridiagonal(lower,diag,upper,rhs),rhs,atol=1e-12)


class PrivacyTests(unittest.TestCase):
    def test_replacement_sensitivity_bounds(self):
        for query in ['Moyenne','Somme','Comptage']:
            d,dp=adjacent_replacement([2.,5.,9.],query,0.,10.,threshold=5.)
            self.assertEqual(len(d),len(dp))
            self.assertEqual(np.count_nonzero(d!=dp),1)
            gap=abs(compute_stats(d,query,5.)-compute_stats(dp,query,5.))
            self.assertLessEqual(gap,compute_sensitivity(query,0.,10.,3)+1e-12)
        # Public fixed-size replacement on both extremal datasets attains the bound.
        for query in ['Moyenne','Somme','Comptage']:
            left=np.zeros(5);right=left.copy();right[0]=10
            gap=compute_stats(right,query,5)-compute_stats(left,query,5)
            self.assertAlmostEqual(gap,compute_sensitivity(query,0,10,5))

    def test_invalid_parameters_never_reveal_exact_value(self):
        for eps in [0.,-1.,float('nan'),float('inf')]:
            with self.assertRaises(ValueError):laplace_mechanism(10.,1.,eps)
        for eps,delta in [(1.,1e-5),(.5,0),(.5,1),(.5,float('nan'))]:
            with self.assertRaises(ValueError):gaussian_scale(1.,eps,delta)
        with self.assertRaises(ValueError):compute_stats([[1,2],[3,4]],'Moyenne')
        with self.assertRaises(ValueError):compute_stats([float('nan')],'Moyenne')

    def test_laplace_density_ratio_bound(self):
        from verification import log_density
        sensitivity=3.;eps=.7;scale=sensitivity/eps
        z=np.linspace(-100,100,1001)
        loss=log_density(z,2.,scale,'Laplace')-log_density(z,5.,scale,'Laplace')
        self.assertLessEqual(np.max(np.abs(loss)),eps+1e-12)

    def test_diagnostic_zero_gap_and_seed(self):
        result=distribution_diagnostic(2.,2.,1.,'Laplace',rng=np.random.default_rng(42))
        self.assertEqual(result['accuracy'],.5)
        first=distribution_diagnostic(2.,5.,1.,'Laplace',rng=np.random.default_rng(42))
        second=distribution_diagnostic(2.,5.,1.,'Laplace',rng=np.random.default_rng(42))
        self.assertEqual(first['accuracy'],second['accuracy'])
        expected=1-.5*np.exp(-3/2)
        self.assertLess(abs(first['accuracy']-expected),5*first['stderr'])

    def test_calibrated_gaussian_scale_and_reproducibility(self):
        scale=gaussian_scale(2.,.5,1e-5)
        self.assertGreater(scale,2*np.sqrt(2*np.log(1.25/1e-5))/.5)
        a=gaussian_mechanism_from_eps_delta(3.,2.,.5,1e-5,np.random.default_rng(42))
        b=gaussian_mechanism_from_eps_delta(3.,2.,.5,1e-5,np.random.default_rng(42))
        self.assertEqual(a,b)


class StochasticTests(unittest.TestCase):
    def test_brownian_variance(self):
        _,w=brownian(T=2.,steps=20,paths=20000,rng=np.random.default_rng(42))
        self.assertLess(abs(w[:,-1].mean()),.04)
        self.assertLess(abs(w[:,-1].var()-2.),.08)

    def test_additive_solution_uses_same_brownian(self):
        _,w=brownian(paths=5,steps=100,rng=np.random.default_rng(42))
        # Brownian draws are path-major, Euler draws are time-major; build the
        # exact increment sequence using the latter ordering.
        increments=np.random.default_rng(42).normal(size=(100,5))*.1
        t,x=euler_eds(lambda x:.5,lambda x:1.,0.,1.,5,M=100,rng=np.random.default_rng(42))
        expected=t[None,:]+.5*np.column_stack((np.zeros(5),np.cumsum(increments,axis=0).T))
        np.testing.assert_allclose(x,expected,atol=1e-12)

    def test_square_root_scheme_has_no_spurious_half_unit_drift(self):
        _,x=euler_eds(np.sqrt,lambda x:np.zeros_like(x),1.,1.,20000,M=200,mode='full_truncation',rng=np.random.default_rng(42))
        self.assertTrue(np.all(x>=0))
        self.assertLess(abs(x[:,-1].mean()-1.),.04)

    def test_coupled_gbm_refinement_and_repeatability(self):
        r=gbm_convergence(steps=(20,40,80,160,320),paths=2000,seed=42)
        repeat=gbm_convergence(steps=(20,40,80,160,320),paths=2000,seed=42)
        np.testing.assert_array_equal(r.euler_error,repeat.euler_error)
        self.assertLess(r.euler_error[-1],r.euler_error[0])
        self.assertLess(r.milstein_error[-1],r.euler_error[-1])
        self.assertGreater(r.euler_slope,.3);self.assertLess(r.euler_slope,.8)
        self.assertGreater(r.milstein_slope,.7);self.assertLess(r.milstein_slope,1.3)

    def test_import_has_no_experiments(self):
        spec=importlib.util.spec_from_file_location('pni_entrypoint',ROOT/'equations_stochastiques'/'code_PNI.py')
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        self.assertTrue(callable(module.main))



class DesktopCallbackTests(unittest.TestCase):
    """Exercise desktop calculation callbacks without creating a Tk window."""
    @staticmethod
    def app():
        from app import DPApp
        class Var:
            def __init__(self,value):self.value=value
            def get(self):return self.value
            def set(self,value):self.value=value
        app=DPApp.__new__(DPApp)
        app.data=np.array([2.,5.,9.])
        for name,value in [('func_var','Moyenne'),('mech_var','Laplace'),('epsilon_var',.5),('delta_var',1e-5),('clip_min_var',0.),('clip_max_var',10.),('threshold_var',5.),('use_manual_sigma',False),('sigma_var',7.)]:
            setattr(app,name,Var(value))
        app._display_results=lambda:None
        app._plot_comparison=lambda:None
        return app

    def test_manual_gaussian_scale_used_by_diagnostic(self):
        app=self.app();app.mech_var.set('Gaussien');app.use_manual_sigma.set(True)
        self.assertEqual(app._parameters()[5],7.)
        app.sigma_var.set(3.)
        self.assertEqual(app._parameters()[5],3.)

    def test_callbacks_recompute_current_statistics(self):
        from unittest.mock import patch
        app=self.app();app.run_calculation()
        self.assertAlmostEqual(app.true_value,16/3)
        app.data=np.array([1.,1.,1.]);app.run_calculation()
        self.assertEqual(app.true_value,1.)
        with patch('app.distribution_diagnostic',return_value={'accuracy':.5,'ci95':(.5,.5)}) as diagnostic,patch.object(app,'_show_diagnostic'):
            app.verify_dp()
            self.assertEqual(diagnostic.call_args.args[0],1.)

    def test_invalid_calculation_is_reported(self):
        from unittest.mock import patch
        app=self.app();app.clip_min_var.set(20.)
        with patch('app.messagebox.showerror') as error:
            app.run_calculation()
            error.assert_called_once()

if __name__=='__main__':unittest.main()
