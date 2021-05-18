#!/usr/bin/env python3
'''
Solve initial value problem to get drift paths using pytorch
'''

import numpy
from scipy.integrate import solve_ivp
from scipy.interpolate import RegularGridInterpolator as RGI
from pochoir import units

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
        self.domain = domain

        self.calls = 0

        for dim in range(len(domain.shape)):
            start = origin[dim]
            stop  = origin[dim] + shape[dim] * spacing[dim]
            rang = numpy.arange(start, stop, spacing[dim])
            print ("interp dim:", dim, rang.shape, vfield[dim].shape)
            points.append(rang)

        self.interp = [
            RGI(points, component)
            for component in vfield]

    def __call__(self, time, pos):
        '''
        Return velocity vector at location (time independent).
        '''
        print(f'drift:{self.calls:4d}: t={time/units.us:.3f} us, r={pos/units.mm} mm')
        velo = numpy.zeros_like(pos)
        speed_unit = units.mm/units.us
        for ind, inter in enumerate(self.interp):
            try:
                got = inter([pos])
            except ValueError as err:
                print(f'v_{ind}(t={time/units.us:.3f}us, r=@{pos/units.mm} mm)')
                o = self.domain.origin
                e = o + self.domain.spacing * self.domain.shape
                print(f'{o/units.mm} mm -> {e/units.mm} mm')

                raise
            got = got[0]
            print(f'\tv_{ind}(t={time/units.us:.3f}us, r=@{pos}) = {got/speed_unit:.3f} mm/us')
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
    print(f'start @{start}, times={times/units.us}')
    func = Simple(domain, velocity)
    #res = odeint(func, start, times, rtol=0.01, atol=0.01)
    res = solve_ivp(func, [times[0], times[-1]], start, t_eval=times,
                    rtol=0.0001, atol=0.0001,
                    method='Radau',
                    #max_step=0.1
                    )
    print(f"function called {func.calls} times")
    return res['y'].T
