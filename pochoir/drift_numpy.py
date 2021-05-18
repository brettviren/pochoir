#!/usr/bin/env python3
'''
Solve initial value problem to get drift paths using pytorch
'''

import numpy
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
        shape = domain.shape
        spacing = domain.spacing
        origin = domain.origin
        points = list()

        self.calls = 0

        for dim in range(len(domain.shape)):
            start = origin[dim]
            stop  = origin[dim] + shape[dim] * spacing[dim]
            rang = numpy.arange(start, stop, spacing[dim])
            #print ("interp dim:",dim,rang.shape,vfield[dim].shape)
            points.append(rang)

        self.interp = [
            RGI(points, component)
            for component in vfield]

    def __call__(self, tpoint, tick):
        '''
        Return velocity vector at location (time independent).

        Note: scipy version wants point as first, time as second
        argument.  This differs from torch version.
        '''
        print(f'drift: {tpoint} {tick}')
        velo = numpy.zeros_like(tpoint)
        for ind, inter in enumerate(self.interp):
            got = inter(tpoint)
            velo[ind] = got

        self.calls += 1
        return velo


def solve(domain, start, velocity, times):
    '''
    Return the path of points at times from start through velocity field.
    '''
    start = numpy.array(start)
    velocity = [numpy.array(v) for v in velocity]
    times = numpy.array(times)
    print(f'start:{start}')
    func = Simple(domain, velocity)
    res = odeint(func, start, times, rtol=0.01, atol=0.01)
    print(f"function called {func.calls} times")
    return res
