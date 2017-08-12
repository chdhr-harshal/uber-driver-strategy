#!/usr/local/bin/python

from __future__ import division
import numpy as np
from scipy.optimize import minimize

class Bisection(object):
    """
    Bisection algorithm class
    """
    def __init__(self, beta, f, v):
        self.beta = beta

        self.f = f
        self.v = v

    def solve_inner_problem(self):
        bounds = tuple([(0,1) for i in xrange(len(self.v))])

        cons = ({'type':'ineq',
                'fun': lambda p: np.array(p)},
                {'type':'ineq',
                'fun': lambda p: self.f.dot(np.log(np.array(p))) - self.beta},
                {'type': 'eq',
                'fun': lambda p: np.sum(np.array(p)) -1})

        p0 = [1/len(self.f) for i in self.f]
        sol = minimize(self.objective,
                    p0,
                    bounds=bounds,
                    constraints=cons)
                    # tol=1e-1)
                    # options={'maxiter':100})

        print "p: {}".format(sol.x)
        print "f: {}".format(self.f)
        print "v: {}".format(self.v)
        print "value: {}".format(sol.fun)

        return sol.fun

    def objective(self, p):
        p = np.array(p)
        return p.dot(self.v)
