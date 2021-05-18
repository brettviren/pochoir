#!/usr/bin/env python3
'''
Apply FDM solution to solve Laplace boundary value problem using numpy
'''

import cupy
from pochoir.fdm_numpy import solve as solve_numpy
from pochoir.fdm_generic import stencil

from pochoir import arrays

from .fdm_generic import edge_condition, stencil
    

def solve(iarr, barr, periodic, prec, epoch, nepochs,
          stencil = stencil):
    '''
    Solve boundary value problem

    Return (arr, err)

        - iarr gives array of initial values

        - barr gives bool array where True indicates value at that
          index is boundary (imutable).

        - periodic is list of Boolean.  If true, the corresponding
          dimension is periodic, else it is fixed.

        - epoch is number of iteration per precision check

        - nepochs limits the number of epochs

    Returned arrays "arr" is like iarr with updated solution including
    fixed boundary value elements.  "err" is difference between last
    and penultimate iteration.
    '''
    iarr = cupy.array(iarr)
    barr = cupy.array(barr)

    bi_core = cupy.array(iarr*barr)
    mutable_core = cupy.invert(barr)
    tmp_core = cupy.zeros(iarr.shape)

    err = cupy.zeros_like(iarr)

    barr_pad = cupy.pad(barr, 1)
    iarr_pad = cupy.pad(iarr, 1)

    # Get indices of fixed boundary values and values themselves
    ifixed = barr_pad == True
    fixed = iarr_pad[ifixed]
    core = arrays.core_slices1(iarr_pad)

    prev = None
    for iepoch in range(nepochs):
        print(f'epoch: {iepoch}/{nepochs} x {epoch}')
        for istep in range(epoch):
            #print(f'step: {istep}/{epoch}')
            if epoch-istep == 1: # last in the epoch
                prev = cupy.array(iarr_pad[core])

            stencil(iarr_pad, tmp_core)

            iarr_pad[core] = bi_core + mutable_core*tmp_core

            edge_condition(iarr_pad, *periodic)
            
            if epoch-istep == 1: # last in the epoch
                err = iarr_pad[core] - prev
                maxerr = cupy.max(cupy.abs(err))
                #print(f'maxerr: {maxerr}')
                if prec and maxerr < prec:
                    print(f'fdm reach max precision: {prec} > {maxerr}')
                    return (iarr_pad[core], err)

    print(f'fdm reach max epoch {epoch} x {nepochs}, last prec {prec} < {maxerr}')
    res = (iarr_pad[core], err)
    return tuple([r.get() for r in res])


# def solve(iarr, barr, periodic, prec, epoch, nepochs,
#           stencil = stencil):
#     iarr = cupy.array(iarr)
#     barr = cupy.array(barr)

#     res = solve_numpy(iarr, barr, periodic, prec, epoch, nepochs,
#                       stencil = stencil)
#     return tuple([r.get() for r in res])
