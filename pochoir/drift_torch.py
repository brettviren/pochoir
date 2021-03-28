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
        points = list()
        for num, spacing, origin in zip(domain.shape, domain.spacing, domain.origin):
            start = origin 
            stop  = origin + num * spacing
            points.append(torch.arange(start, stop, spacing))
            
        self.interp = [
            ti.RegularGridInterpolator(points, coord)
            for coord in vfield]

    def __call__(self, tick, tpoint):
        '''
        Return velocity vector at location (time independent).

        Location is given as an index (but floating point) vector.
        '''
        velo = torch.zeros_like(tpoint)

        point = [torch.tensor([t]) for t in tpoint]

        for ind, inter in enumerate(self.interp):
            velo[ind] = inter(point)[0]
        
        return velo


def solve(domain, start, velocity, times):
    '''
    Return the path of points at times from start through velocity field.
    '''
    start = to_torch(start)
    velocity = to_torch(velocity)
    times = to_torch(times)
    print(times.shape)
    func = Simple(domain, velocity)
    return odeint(func, start, times)
    
