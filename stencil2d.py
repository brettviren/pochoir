#!/usr/bin/env python

from pochoir import *

import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
# The domain.  In a real problem this will be very large and we should
# limit the number of dense arrays of this shape.
shape=(2000,2000)

def es_boundary_values(arr):
    s = arr.shape
    arr[0,:] = 1000
    hw = s[0]//2
    arr[hw+2, 0:s[0]:2] = 200
    arr[hw, 0:s[0]:2] = -200
    arr[-1,:] = 0
def w1_boundary_values(arr):
    s = arr.shape
    arr[0,:] = 0
    hw = s[0]//2
    arr[hw+2, 0:s[0]:2] = 0
    arr[hw+2, 4] = 1
    arr[hw, 0:s[0]:2] = -0
    arr[-1,:] = 0
def w2_boundary_values(arr):
    s = arr.shape
    arr[0,:] = 0
    hw = s[0]//2
    arr[hw+2, 0:s[0]:2] = 0
    arr[hw, 0:s[0]:2] = -0
    arr[hw, 4] = 1
    arr[-1,:] = 0
def toy_boundary_values(arr):
    s = arr.shape
    arr[:10,:] = 1000
    arr[:,:10] = 1000

    arr[200,200] = -1000
    arr[200,210] = -1000
    arr[210,200] = -1000
    arr[210,210] = -1000

    arr[1200,200] = 3000
    arr[1200,210] = 3000
    arr[1210,200] = 3000
    arr[1210,210] = 3000

    arr[200,1200] = -1000
    arr[200,1210] = -1000
    arr[210,1200] = -1000
    arr[210,1210] = -1000

    arr[-20:-1,:] = 1000
    arr[:,-20:-1] = -1000


def boundary_values(arr):
    toy_boundary_values(arr)
    edge_conditions2d(arr, "periodic", "fixed" )

def subarray(arr, i, j):
    sa = arr[1+i:1+i+shape[0],
             1+j:1+j+shape[1]]
    return sa

phi1 = make_domain(shape)
phi2 = make_domain(shape)
phi1 = togpu(phi1)
phi2 = togpu(phi2)

boundary_values(phi1)

def plotit(grid, title=""):
    plt.clf()
    plt.title(title)
    plt.imshow(tocpu(grid), interpolation='none', aspect='auto')
    plt.colorbar()
    pdf.savefig()

with PdfPages('stencil2d.pdf') as pdf:
    nsteps = 5000
    toplot = 1000
    for step in range(nsteps):

        # if step==0 or step%toplot == 0:
        #     plotit(phi1, f'solution (step {step})')

        phi2[1:-1, 1:-1] = phi1[1:-1, 1:-1]

        # stencil reduces by 2, save back to "core"
        phi1[1:-1, 1:-1] = stencil2d(phi1)

        # if step==0 or step%toplot == 0:
        #     plotit(phi1, f'solution (step {step}+1)')

        # restore boundary
        boundary_values(phi1)
        
        if step==0 or step%toplot == 0:
            plotit(phi1, f'solution (step {step}+1)')

        if step==0 or step%toplot == 0:
            err = phi1 - phi2
            abserr = arrays.abs(err)
            maxerr = arrays.max(abserr)
            toterr = arrays.sum(abserr)
            print(f'{step}: maxerr:{maxerr} avgerr:{toterr}')

