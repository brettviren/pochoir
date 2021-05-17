#!/usr/bin/env python3
'''
Apply FDM solution to solve Laplace boundary value problem using numpy
like arrays.  Some things are also called from fdm_cupy.
'''

from pochoir import arrays

from .fdm_generic import edge_condition, stencil
    
def set_core1(dst, src, core):
    dst[core] = src

def set_core2(dst, src, core):
    dst[core] = src

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
    amod = arrays.module(iarr)

    err = amod.zeros_like(iarr)

    barr = amod.pad(barr, 1)
    iarr = amod.pad(iarr, 1)

    # Get indices of fixed boundary values and values themselves
    ifixed = barr == True
    fixed = iarr[ifixed]
    core = arrays.core_slices1(iarr)

    prev = None
    for iepoch in range(nepochs):
        print(f'epoch: {iepoch}/{nepochs} x {epoch}')
        for istep in range(epoch):
            #print(f'step: {istep}/{epoch}')
            if epoch-istep == 1: # last in the epoch
                prev = amod.array(iarr[core])

            tmp = stencil(iarr)
            set_core1(iarr, tmp, core)
            set_core2(iarr, fixed, ifixed)
            edge_condition(iarr, *periodic)
            
            if epoch-istep == 1: # last in the epoch
                err = iarr[core] - prev
                maxerr = amod.max(amod.abs(err))
                #print(f'maxerr: {maxerr}')
                if prec and maxerr < prec:
                    print(f'fdm reach max precision: {prec} > {maxerr}')
                    return (iarr[core], err)

    print(f'fdm reach max epoch {epoch} x {nepochs}, last prec {prec} < {maxerr}')
    return (iarr[core], err)

