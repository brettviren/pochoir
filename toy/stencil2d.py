#!/usr/bin/env python
import os
import sys
import time
import numpy
import pochoir


try:
    arrays = sys.argv[1]
except IndexError:
    arrays = "numpy"

if arrays == "torch":
    amod = pochoir.Torch()
else:
    amod = pochoir.Numpy()
print(f'Using {arrays}')

try:
    nsteps = int(sys.argv[2])
except:
    nsteps = 50000
ntoplot = nsteps // 5

print(f'{nsteps} steps')



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
    pochoir.edge_conditions2d(arr, "periodic", "fixed" )

phi1 = pochoir.make_domain(amod, shape)
phi2 = pochoir.make_domain(amod, shape)
bv = pochoir.make_domain(amod, shape)

boundary_values(phi1)
boundary_values(bv)
tocalc = bv == 0.

def plotit(arr, title=""):
    plt.clf()
    plt.title(title)
    plt.imshow(arr, interpolation='none', aspect='auto')
    plt.colorbar()
    pdf.savefig()

toplot = list()

start_time = time.time()
for step in range(nsteps):

    if step==0:
        toplot.append((f'solution {step}', amod.tocpu(phi1[1:-1, 1:-1])))

    # save pre-update solution, if we want to check error
    if step>1 and step%ntoplot == 0:
        phi2[1:-1, 1:-1] = phi1[1:-1, 1:-1]

    # update
    phi1[1:-1, 1:-1] = pochoir.stencil2d(phi1)
    boundary_values(phi1)

    if step>1 and step%ntoplot == 0:
        err = phi1 - phi2
        abserr = amod.abs(err)
        toplot.append((f'error {step}', amod.tocpu(abserr[1:-1, 1:-1])))
        toplot.append((f'solution {step}', amod.tocpu(phi1[1:-1, 1:-1])))
        maxerr = amod.max(abserr[tocalc])
        dt = time.time() - start_time
        print(f'{step}: maxerr:{maxerr} dt:{dt}')

stop_time = time.time()
dt = stop_time - start_time
hz = nsteps/dt
print(f'nsteps:{nsteps} dt:{dt}s ({hz:.1f} Hz)')

fname = f'stencil2d-{nsteps}-{arrays}.npz'
print(f'saving {fname}')
numpy.savez(fname, solution=toplot[-1][1], error=toplot[-2][1])

eps = 1e-8
fname = f'stencil2d-{nsteps}-{arrays}.pdf'
print(f'printing {fname}')
with PdfPages(fname) as pdf:
    for tit, arr in toplot:
        if tit.startswith("solution"):
            plotit(arr, tit)
        else:
            arr[arr<eps] = eps
            plotit(numpy.log10(arr), tit)
