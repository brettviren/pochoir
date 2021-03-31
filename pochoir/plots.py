#!/usr/bin/env python3
'''
Make plots.
'''
from . import arrays

# restrict imports to numpy + matplotlib.  No domain operations!
import numpy
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

def image(arr, fname, domain, title=""):
    if len(arr.shape) != 2:
        raise ValueError("image plots take 2D arrays")

    arr = arrays.to_numpy(arr)
    plt.clf()

    extent = None
    if domain:
        extent = domain.imshow_extent()
    plt.title(title)
    plt.imshow(arr, interpolation='none', aspect='auto',
               extent = extent)
    plt.colorbar()

    plt.savefig(fname)

def quiver(varr, fname, domain):
    varr = [arrays.to_numpy(a) for a in varr]
    ndim = len(varr)
    if ndim not in (2,3):
        raise ValueError("quiver plots take vector of 2D or 3D arrays")

    mg = domain.meshgrid

    plt.clf()
    if ndim == 2:               # 2D
        plt.quiver(mg[0], mg[1],
                   varr[0], varr[1], units='xy')
    else:                       # 3D
        fig = plt.figure()
        ax = fig.gca(projection='3d')

        ax.quiver(mg[0], mg[1], mg[2],
                  varr[0], varr[1], varr[2],
                  length=domain.spacing[0], normalize=True)
    plt.savefig(fname)
