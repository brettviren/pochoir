#!/usr/bin/env python3
'''
Make plots.
'''
from . import arrays
from pathlib import Path
import numpy
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

# fixme: instead of passing in a file name just so this can be called,
# the caller in __main__.py should handle saving.
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

    # extent = None
    # if domain:
    #     extent = domain.imshow_extent()
    #X,Y = domain.meshgrid
    Y,X = numpy.meshgrid(*domain.linspaces, indexing="ij")

    plt.title(title)
    print(f'plotting: {arr.shape} {fname}')
    #plt.imshow(arr, interpolation='none', aspect='auto',
    #           extent = extent)
    plt.pcolormesh(X, Y, arr, shading='auto')
    #plt.imshow(arr, interpolation='none', aspect='auto')
    plt.colorbar()
    savefig(fname)

def set_limits(limits):
    if not limits:
        return
    xlim, ylim = limits
    if xlim is not None:
        plt.xlim(*xlim)
    if ylim is not None:
        plt.ylim(*ylim)


def quiver(varr, fname, domain, step=1, limits=None, scale=1.0):
    '''
    Plot a vector field.

    step determines the amount of decimation.
    '''
    varr = [arrays.to_numpy(a) for a in varr]
    ndim = len(varr)
    if ndim not in (2,3):
        raise ValueError("quiver plots take vector of 2D or 3D arrays")


    mg = numpy.meshgrid(*domain.linspaces, indexing="ij")
    print (f'meshgrid: {mg[0].shape} -> {mg[1].shape}')

    # possibly decimate
    slcs = tuple([slice(0,s,step) for s in varr[0].shape])

    plt.clf()
    if ndim == 2:               # 2D
        plt.quiver(mg[1][slcs], mg[0][slcs],
                   varr[1][slcs], varr[0][slcs],
                   scale=scale, units='xy')
        set_limits(limits)
            
    else:                       # 3D
        fig = plt.figure()
        ax = fig.gca(projection='3d')

        ax.quiver(mg[0][slcs], mg[1][slcs], mg[2][slcs],
                  varr[0][slcs], varr[1][slcs], varr[2][slcs],
                  length=domain.spacing[0], normalize=True)
        set_limits(limits)

    savefig(fname)

def drift2d(paths, output, domain, trajectory):
    '''
    Plot 2D drift paths
    '''
    for path in paths:
        plt.scatter(path[:,1], path[:,0])
    savefig(output)

def drift3d(varr, fname, domain, trajectory):
    '''
    Plot 3D drift paths
    '''
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
