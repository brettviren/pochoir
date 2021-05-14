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
    plt.savefig(path.resolve(), dpi=600)

def signedlog(arr, eps = 1e-5, scale=None):
    '''
    Apply the "signed log" transform to an array.

    Result is +/-log10(|arr|*scale) with the sign of arr preserved in
    the result and any values that are in eps of zero set to zero.

    If scale is not given then 1/eps is used.
    '''
    if not scale:
        scale = 1/eps

    shape = arr.shape
    arr = numpy.array(arr).reshape(-1)
    arr[numpy.logical_and(arr < eps, arr > -eps)] = 0.0
    pos = arr>eps
    neg = arr<-eps
    arr[pos] = numpy.log10(arr[pos]*scale)
    arr[neg] = -numpy.log10(-arr[neg]*scale)
    return arr.reshape(shape)

def image(arr, fname, domain, title="", scale="linear"):
    if len(arr.shape) != 2:
        raise ValueError("image plots take 2D arrays")

    arr = arrays.to_numpy(arr)
    if scale == "signedlog":
        arr = signedlog(arr)

    plt.clf()

    extent = None
    if domain:
        extent = domain.imshow_extent()
    plt.title(title)
    print(f'plotting: {arr.shape} {fname}')
    #plt.imshow(arr, interpolation='none', aspect='auto',
    #           extent = extent)
    plt.imshow(arr, interpolation='none', aspect='auto')

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
