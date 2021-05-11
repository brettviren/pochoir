#!/usr/bin/env python3
'''
Make plots.
'''
from . import arrays
from pathlib import Path
import numpy
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

def savefig(fname):
    path = Path(fname)
    if not path.parent.exists():
        path.parent.mkdir(parents=True)
    plt.savefig(path.resolve())

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

    savefig(fname)

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
    savefig(fname)

def drift(varr, fname, domain, trajectory):
    varr = [arrays.to_numpy(a) for a in varr]
    ndim = len(varr)
    mg = domain.meshgrid
    plt.clf()
    fig = plt.figure()
    ax = fig.gca(projection='3d')
    ax.set_xlim3d(0,domain.shape[0]*domain.spacing[0])
    ax.set_ylim3d(0,domain.shape[1]*domain.spacing[1])
    ax.set_zlim3d(0,domain.shape[2]*domain.spacing[2])
    if(len(varr)<trajectory):
        raise ValueError("Not enough trajectories to plot")
    if(trajectory==-1):
        xdata,ydata,zdata = varr[0][:,0],varr[0][:,1],varr[0][:,2]
        ax.plot3D(xdata,ydata,zdata)
    else:
        for i in range(trajectory):
            xdata,ydata,zdata = varr[i][:,0],varr[i][:,1],varr[i][:,2]
            ax.plot3D(xdata,ydata,zdata)
    savefig(fname)
