#!/usr/bin/env python3
'''
Apply FDM solution to solve Laplace boundary value problem
'''

from . import arrays

def edge_condition(arr, *periodic):
    '''
    Apply N edge conditions (periodic if True, else fixed) to N-D array.
    '''
    np = len(periodic)
    na = len(arr.shape)
    if np != na:
        raise ValueError(f"dimension mismatch: {np} != {na}")
    
    # whole array slice
    slices = [slice(0,s) for s in arr.shape]
    for dim, per in enumerate(periodic):
        n = arr.shape[dim]
        src1 = list(slices)
        src2 = list(slices)
        dst1 = list(slices)
        dst2 = list(slices)

        dst1[dim] = slice(0,1)
        src1[dim] = slice(n-2, n-1)

        dst2[dim] = slice(n-1,n)
        src2[dim] = slice(1,2)

        if per:
            arr[tuple(dst1)] = arr[tuple(src1)]
            arr[tuple(dst2)] = arr[tuple(src2)]
        else:                   # fixed
            arr[tuple(dst1)] = arr[tuple(src2)]
            arr[tuple(dst2)] = arr[tuple(src1)]


def stencil(array):
    '''
    Return sum of 2N views of N-D array.

    Each view for a dimension is offset by +/- one cell.
    '''
    # whole array slice
    slices = [slice(1,s-1) for s in array.shape]
    nd = len(slices)
    norm = 1/(2*nd)

    amod = arrays.module(array)
    core_shape = [s-2 for s in array.shape]
    res = amod.zeros(core_shape)

    for dim, n in enumerate(array.shape):
        pos = list(slices)
        pos[dim] = slice(2,n)
        res += array[tuple(pos)]

        neg = list(slices)
        neg[dim] = slice(0,n-2)
        res += array[tuple(neg)]

    return norm * res
    

def solve(iarr, barr, periodic, prec, epoch, nepochs):
    '''
    Solve boundary value problem

    Return (arr, err)

        - iarr gives array of initial values

        - barr gives array which is non-zero on fixed boundary values

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

    barr = arrays.pad1(barr)
    iarr = arrays.pad1(iarr)
    core = arrays.core_slices1(iarr)

    # Get indices of fixed boundary values and values themselves
    ifixed = barr != 0
    fixed = iarr[ifixed]

    prev = None
    for iepoch in range(nepochs):
        #print(f'epoch: {iepoch}')
        for istep in range(epoch):
            #print(f'step: {istep}/{epoch}')
            if epoch-istep == 1: # last in the epoch
                prev = arrays.dup(iarr[core])

            iarr[core] = stencil(iarr)
            iarr[ifixed] = fixed
            edge_condition(iarr, *periodic)
            
            if epoch-istep == 1: # last in the epoch
                err = iarr[core] - prev
                maxerr = amod.max(amod.abs(err))
                #print(f'maxerr: {maxerr}')
                if prec and maxerr < prec:
                    return (iarr[core], err)

    return (iarr[core], err)
