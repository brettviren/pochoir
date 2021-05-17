#!/usr/bin/env python3
'''
Apply FDM solution to solve Laplace boundary value problem using numba
with CUDA.
'''
import math
import numba
import cupy
from numba import cuda
from pochoir import arrays
from .fdm_generic import edge_condition

@cuda.jit
def stencil_numba2d_jit(arr, out):
    i, j = cuda.grid(2)
    n, m = arr.shape
    if 1 <= i < n - 1 and 1 <= j < m - 1:
        out[i, j] = (1/4.0)*(
            arr[i - 1, j] + arr[i, j - 1] +
            arr[i + 1, j] + arr[i, j + 1])
        
@cuda.jit
def stencil_numba3d_jit(arr, out):
    i, j, k = cuda.grid(2)
    l, n, m = arr.shape
    if 1 <= i < l - 1 and 1 <= j < n - 1 and 1 <= k < m - 1:
        out[i, j, k] = (1/6.0)*(
            arr[i-1, j, k] + arr[i, j-1, k] + arr[i, j, k-1] +  
            arr[i+1, j, k] + arr[i, j+1, k] + arr[i, j, k+1])


def stencil(arr, out):
    out[:] = 0

    if arr.ndim == 2:
        threadsperblock = (32, 32)
        blockspergrid_x = math.ceil(arr.shape[0] / threadsperblock[0])
        blockspergrid_y = math.ceil(arr.shape[1] / threadsperblock[1])
        blockspergrid = (blockspergrid_x, blockspergrid_y)
        stencil_numba2d_jit[blockspergrid, threadsperblock](arr, out)
        return

    threadsperblock = (16, 16, 16)
    blockspergrid_x = math.ceil(arr.shape[0] / threadsperblock[0])
    blockspergrid_y = math.ceil(arr.shape[1] / threadsperblock[1])
    blockspergrid_z = math.ceil(arr.shape[2] / threadsperblock[2])
    blockspergrid = (blockspergrid_x, blockspergrid_y, blockspergrid_z)
    stencil_numba3d_jit[blockspergrid, threadsperblock](arr, out)
    return
    


from pochoir.fdm_numpy import solve as solve_numpy
def solve(iarr, barr, periodic, prec, epoch, nepochs,
          stencil = stencil):



    iarr_pad = cupy.pad(cupy.array(iarr), 1)
    barr_pad = cupy.pad(cupy.array(barr), 1)
    bi_pad = cupy.pad(cupy.array(iarr*barr), 1)
    mutable_pad = cupy.pad(cupy.invert(cupy.array(barr)), 1)

    tmp_pad = cupy.zeros_like(iarr_pad)

    err = cupy.zeros_like(iarr)

    # Get indices of fixed boundary values and values themselves
    core = arrays.core_slices1(iarr_pad)

    prev = None
    for iepoch in range(nepochs):
        print(f'epoch: {iepoch}/{nepochs} x {epoch}')

        for istep in range(epoch):
            #print(f'step: {istep}/{epoch}')
            if epoch-istep == 1: # last in the epoch
                prev = cupy.array(iarr_pad)

            stencil(iarr_pad, tmp_pad)

            iarr_pad = bi_pad + mutable_pad*tmp_pad
            edge_condition(iarr_pad, *periodic)
            
            if epoch-istep == 1: # last in the epoch
                err = iarr_pad - prev
                maxerr = cupy.max(cupy.abs(err))
                #print(f'maxerr: {maxerr}')
                if prec and maxerr < prec:
                    print(f'fdm reach max precision: {prec} > {maxerr}')
                    return (iarr_pad[core], err[core])

    print(f'fdm reach max epoch {epoch} x {nepochs}, last prec {prec} < {maxerr}')
    res = (iarr_pad[core], err[core])
    return tuple([r.get() for r in res])


