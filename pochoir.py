#!/usr/bin/env python3

import numpy

class Torch:
    def __init__(self, mod=None):
        if not mod:
            import torch
            mod = torch
        self.mod = mod 

    def tocpu(self, array):
        return array.to('cpu').numpy()
    def togpu(self, array):
        return array.to('cuda')

    def __getattr__(self, key):
        return getattr(self.mod, key)

class Numpy:
    def __init__(self, mod=None):
        if not mod:
            mod = numpy
        self.mod = mod
        
    def tocpu(self, array):
        return self.mod.array(array)
    def togpu(self, array):
        return self.mod.array(array)

    def __getattr__(self, key):
        return getattr(self.mod, key)


def make_domain(arrays, shape):
    '''Return a domain grid object with target area of the given shape.

    Target is indexed along one dimension as [1:-1]
    '''
    padded = [s+2 for s in shape]
    return arrays.togpu(arrays.zeros(padded))

def edge_conditions1d(grid, *cond):
    if cond[0] == "periodic":
        grid[0] = grid[-2]
        grid[-1] = grid[1]
    if cond[0] == "fixed":
        grid[0] = grid[1]
        grid[-1] = grid[-2]
        
def edge_conditions2d(grid, *cond):
    if cond[0] == "periodic":
        grid[ 0,:] = grid[-2,:]
        grid[-1,:] = grid[ 1,:]
    if cond[0] == "fixed":
        grid[ 0,:] = grid[ 1,:]
        grid[-1,:] = grid[-2,:]
    if cond[1] == "periodic":
        grid[:, 0] = grid[:,-2]
        grid[:,-1] = grid[:, 1]
    if cond[1] == "fixed":
        grid[:, 0] = grid[:, 1]
        grid[:,-1] = grid[:,-2]
        
def edge_conditions3d(grid, *cond):
    if cond[0] == "periodic":
        grid[ 0,:,:] = grid[-2,:,:]
        grid[-1,:,:] = grid[ 1,:,:]
    if cond[0] == "fixed":
        grid[ 0,:,:] = grid[ 1,:,:]
        grid[-1,:,:] = grid[-2,:,:]
    if cond[1] == "periodic":
        grid[:, 0,:] = grid[:,-2,:]
        grid[:,-1,:] = grid[:, 1,:]
    if cond[1] == "fixed":
        grid[:, 0,:] = grid[:, 1,:]
        grid[:,-1,:] = grid[:,-2,:]
    if cond[2] == "periodic":
        grid[:,:, 0] = grid[:,:,-2]
        grid[:,:,-1] = grid[:,:, 1]
    if cond[2] == "fixed":
        grid[:,:, 0] = grid[:,:, 1]
        grid[:,:,-1] = grid[:,:,-2]
        
def subarray1d(arr, *sign):
    return arr[1+sign[0]: arr.shape[0]-1+sign[0]]

def subarray2d(arr, *sign):
    return arr[1+sign[0]: arr.shape[0]-1+sign[0],
               1+sign[1]: arr.shape[1]-1+sign[1]]

def subarray3d(arr, *sign):
    return arr[1+sign[0]: arr.shape[0]-1+sign[0],
               1+sign[1]: arr.shape[1]-1+sign[1],
               1+sign[2]: arr.shape[2]-1+sign[2]]

def stencil1d(grid):
    return (1/2)*(subarray1d(grid, -1) + subarray1d(grid, +1))

def stencil2d(grid):
    return (1/4)*(subarray2d(grid, -1, 0) + subarray2d(grid,+1,0) +
                  subarray2d(grid,  0,-1) + subarray2d(grid,0,+1))

def stencil3d(grid):
    return (1/6)*(subarray3d(grid, -1, 0, 0) + subarray3d(grid, +1, 0, 0) +
                  subarray3d(grid,  0,-1, 0) + subarray3d(grid, 0, +1, 0) +
                  subarray3d(grid,  0, 0,-1) + subarray3d(grid, 0, 0, +1))
