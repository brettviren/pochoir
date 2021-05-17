#!/usr/bin/env python3
'''
Apply FDM solution to solve Laplace boundary value problem with torch.
'''

import numpy
import torch
from .arrays import core_slices1

from .fdm_generic import edge_condition, stencil

    
def set_core1(dst, src, core):
    dst[core] = src

def set_core2(dst, src, core):
    dst[core] = src

def solve(iarr, barr, periodic, prec, epoch, nepochs):
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

    err = None

    bi_core = torch.tensor(iarr*barr, requires_grad=False)
    mutable_core = torch.tensor(numpy.invert(barr), requires_grad=False)
    tmp_core = torch.zeros(iarr.shape, requires_grad=False)

    barr_pad = torch.tensor(numpy.pad(barr, 1), requires_grad=False)
    iarr_pad = torch.tensor(numpy.pad(iarr, 1), requires_grad=False)
    core = core_slices1(iarr_pad)

    # Get indices of fixed boundary values and values themselves

    prev = None
    for iepoch in range(nepochs):
        print(f'epoch: {iepoch}/{nepochs} x {epoch}')
        for istep in range(epoch):
            #print(f'step: {istep}/{epoch}')
            if epoch-istep == 1: # last in the epoch
                prev = iarr_pad.clone().detach().requires_grad_(False)

            stencil(iarr_pad, tmp_core)
            iarr_pad[core] = bi_core + mutable_core*tmp_core
            edge_condition(iarr_pad, *periodic)
            
            if epoch-istep == 1: # last in the epoch
                err = iarr_pad[core] - prev[core]
                maxerr = torch.max(torch.abs(err))
                #print(f'maxerr: {maxerr}')
                if prec and maxerr < prec:
                    print(f'fdm reach max precision: {prec} > {maxerr}')
                    return (iarr_pad[core], err)
    print(f'fdm reach max epoch {epoch} x {nepochs}, last prec {prec} < {maxerr}')
    return (iarr_pad[core], err)

