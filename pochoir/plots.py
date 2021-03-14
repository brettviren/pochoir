#!/usr/bin/env python3
'''
Make plots.
'''
from . import arrays

# restrict imports to numpy + matplotlib.  No domain operations!
import numpy
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

def image(arr, fname):
    if len(arr.shape) != 2:
        raise ValueError("image plots take 2D arrays")

    arr = arrays.to_numpy(arr)
    plt.clf()
    #plt.title("initial")
    plt.imshow(arr, interpolation='none', aspect='auto')
    plt.colorbar()
    plt.savefig(fname)

def quiver(arr, fname, domain = None):
    arr = arrays.to_numpy(arr)
    ndim = len(arr.shape) - 1
    if ndim not in (2,3):
        raise ValueError("quiver plots take vector of 2D or 3D arrays")

    if not domain:
        axes = [numpy.arange(size) for size in arr.shape[1:]]
        domain = numpy.array(numpy.meshgrid(*axes))

    if ndim == 2:               # 2D
        plt.quiver(domain[0], domain[1],
                   arr[0], arr[1], units='xy')
    else:                       # 3D
        plt.quiver(domain[0], domain[1], domain[2],
                   arr[0], arr[1], arr[2], units='xy')        
    plt.savefig(fname)
