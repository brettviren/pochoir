#!/usr/bin/env python3
'''
Solve electron motion in Efiled with scipy RK method
'''

import numpy as np
from .arrays import to_numpy
from scipy.integrate import solve_ivp as ode
from scipy.integrate import odeint
from scipy.interpolate import RegularGridInterpolator as RGI

class Simple:
    '''
    Simple ODE calable
    '''
    
    def __init__(self, domain, vfield):
        '''
        The vfield give vector feild on domain.
        '''
        points = list()
        for num, spacing, origin in zip(domain.shape, domain.spacing, domain.origin):
            start = origin
            stop  = origin + num * spacing
            points.append(np.arange(start, stop, spacing))
        self.interp =[RGI(points, coord) for coord in vfield]

    def __call__(self, tick, tpoint):
        '''
        Return velocity vector at location (time independent).

        Location is given as an index (but floating point) vector.
        '''
        velo = np.zeros_like(tpoint)

        point = np.array(tpoint)#[np.array([t]) for t in tpoint]
        
        for ind, inter in enumerate(self.interp):

            velo[ind] = inter(point)[0]
        
        return velo

def solve(domain,start,velocity,times):
    '''
    Return the path of points at times from start through velocity field.
    Using SciPy RK method
    '''
    start = to_numpy(start)
    velocity = to_numpy(velocity)
    times = to_numpy(times)
    func = Simple(domain, velocity)
    return odeint(func,start,times,tfirst=True)


