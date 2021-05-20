#!/usr/bin/env python3
'''
Solve initial value problem to get drift paths using pytorch
'''
import math
import numpy
from scipy.integrate import solve_ivp
from scipy.interpolate import RegularGridInterpolator as RGI
from pochoir import units

class Simple:
    '''
    Simple ODE calable
    '''

    def __init__(self, domain, vfield, verbose=False):
        '''
        The vfield give vector feild on domain.
        '''
        shape = domain.shape
        spacing = domain.spacing
        origin = domain.origin
        points = list()
        self.bb = domain.bb
        self.verbose = verbose
        self.calls = 0

        for dim in range(len(domain.shape)):
            start = origin[dim]
            stop  = origin[dim] + shape[dim] * spacing[dim]
            rang = numpy.arange(start, stop, spacing[dim])
            print ("interp dim:", dim, rang.shape, vfield[dim].shape)
            points.append(rang)

        self.interp = [
            RGI(points, component, fill_value=0.0)
            for component in vfield]

    def inside(self, point):
        for i,p in enumerate(point):
            if p < self.bb[0][i] or p > self.bb[1][i]:
                return False
        return True

    def interpolate(self, pos):
        velo = numpy.zeros_like(pos)        
        for ind, inter in enumerate(self.interp):
            try:
                got = inter([pos])
            except ValueError as err:
                print(f'Interpolation failed at:\n\tv_{ind}(r=@{pos/units.mm} mm)')
                print(f'\tdomain: {self.bb}')
                raise

            velo[ind] = got[0]
        return velo

    def extrapolate(self, pos):
        return numpy.zeros_like(pos)

    def __call__(self, time, pos):
        '''
        Return velocity vector at location (time independent).
        '''
        self.calls += 1
        speed_unit = units.mm/units.us
        if self.inside(pos):
            velo = self.interpolate(pos)
            what = "interp"
        else:
            velo = self.extrapolate(pos)
            what = "extrap"

        vmag = math.sqrt(sum([v*v for v in velo]))
        if self.verbose:
            print(f'{what}:{self.calls:4d}: t={time/units.us:.3f} us, r={pos/units.mm} mm v={velo/speed_unit} vmag={vmag/speed_unit:.3f} mm/us')
        return velo



def solve(domain, start, velocity, times, verbose=False):
    '''
    Return the path of points at times from start through velocity field.
    '''
    start = numpy.array(start)
    velocity = [numpy.array(v) for v in velocity]
    times = numpy.array(times)
    print(f'start @{start}, times={times/units.us}')
    func = Simple(domain, velocity, verbose=verbose)
    #res = odeint(func, start, times, rtol=0.01, atol=0.01)
    res = solve_ivp(func, [times[0], times[-1]], start, t_eval=times,
                    rtol=0.0001, atol=0.0001,
                    method='Radau',
                    #max_step=0.1
                    )
    print(f"function called {func.calls} times")
    return res['y'].T
