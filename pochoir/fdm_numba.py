#!/usr/bin/env python3
'''
Apply FDM solution to solve Laplace boundary value problem using numba
'''
import numba

@numba.stencil
def _lap2d(a):
    return (1/4.0) * (
        a[0, 1] + a[0, -1] +
        a[1, 0] + a[-1, 0]
    )
@numba.stencil
def _lap3d(a):
    return (1.0/6.0) * (
        a[0, 0, 1] + a[0, 0, -1] +
        a[0, 1, 0] + a[0, -1, 0] +
        a[1, 0, 0] + a[-1, 0, 0]
    )
@numba.njit
def stencil_numba2d_jit(a):
    return _lap2d(a)
@numba.njit
def stencil_numba3d_jit(a):
    return _lap3d(a)

def stencil(a):
    if a.ndim == 2:
        a = stencil_numba2d_jit(a)
    else:
        a = stencil_numba3d_jit(a)
    # return "core"
    slices = tuple([slice(1,s-1) for s in a.shape])
    return a[slices]


from pochoir.fdm_numpy import solve as solve_numpy
def solve(iarr, barr, periodic, prec, epoch, nepochs,
          stencil = stencil):
    return solve_numpy(iarr, barr, periodic, prec, epoch, nepochs,
                       stencil = stencil)
