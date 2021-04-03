#!/usr/bin/env python3
'''
Solve initial value problem to get drift paths using pytorch
'''

import torch
import torch.nn as nn
from .arrays import to_torch
import torch_interpolations as ti

from torchdiffeq import odeint

class Simple:
    '''
    Simple ODE calable
    '''

    def __init__(self, domain, vfield):
        '''
        The vfield give vector feild on domain.
        '''
        shape = torch.tensor(domain.shape)
        spacing = torch.tensor(domain.spacing)
        origin = torch.tensor(domain.origin)
        points = list()

        self.calls = 0

        for dim in range(len(domain.shape)):
            start = origin[dim]
            stop  = origin[dim] + shape[dim] * spacing[dim]
            rang = torch.arange(start, stop, spacing[dim])
            #print ("interp dim:",dim,rang.shape,vfield[dim].shape)
            points.append(rang)

        self.interp = [
            ti.RegularGridInterpolator(points, component)
            for component in vfield]

    def __call__(self, tick, tpoint):
        '''
        Return velocity vector at location (time independent).

        Location is given as an index (but floating point) vector.
        '''
        velo = torch.zeros_like(tpoint)
        xy = [t.reshape(-1) for t in tpoint]
        for ind, inter in enumerate(self.interp):
            got = inter(xy)
            velo[ind] = got
        
        #print("interp",tpoint.numpy().tolist(),velo.numpy().tolist())
        self.calls += 1
        return velo


def solve(domain, start, velocity, times):
    '''
    Return the path of points at times from start through velocity field.
    '''
    start = to_torch(start)
    velocity = [to_torch(v) for v in velocity]
    times = to_torch(times)
    func = Simple(domain, velocity)
    print(f"starting path at {start}")
    res = odeint(func, start, times, rtol=0.01, atol=0.01)
    print(f"function called {func.calls} times")
    return res
