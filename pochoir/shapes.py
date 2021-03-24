#!/usr/bin/env python3
'''
Shape grid "painting" functions.

These functions set grid points to values.  Functions are called in
terms of grid indicies (eg center) and any distance is in units of the
grid spacing.

Something else must translate from spatial dimensions to indicies, if
that is required.
'''
import numpy
from math import sqrt, floor


def known(ndim):
    if ndim == 2:
        return ("rectangle", "circle")
    if ndim == 3:
        return ("box", "cylinder")
    raise ValueError(f'Unsupported dnumber of dimensions: {ndim}')

def rectangle(dom, arr, value, point1, point2):
    '''
    Paint array inside rectangle defined by two boints with value.
    '''
    if not all([point1, point2]):
        raise ValueErorr(f'rectangle requires both points defined')
    point1 = dom.index(point1)
    point2 = dom.index(point2)

    s = [dom.crop(slice(point1[a], point2[a]), axis=a) for a in [0,1]]
    print (f'rectangle: {point1}->{point2}: {value} -> {s}')
    arr[tuple(s)] = value


def circle(dom, arr, value, radius, center):
    '''
    Paint array inside circle with value subject to domain.

    Circle is given by radius and center in spatial units.
    '''
    center = numpy.array(center)
    # we cheat and move the circle onto the grid
    icen = dom.index(center)

    # number of grid points on either of center along each axis
    irad = int(round(radius / dom.spacing[0]))

    # bounding of circle on axis
    ibb = dom.crop(slice(icen[0]-irad, icen[0]+irad+1), axis=0)

    for i in range(ibb.start, ibb.stop):
        ir = icen[0] - i        # back to relative radius in index
        h = radius**2 - (ir*dom.spacing[0])**2
        if h < 0:
            continue
        hj = int(floor(sqrt(h)/dom.spacing[1]))
        jslc = dom.crop(slice(icen[1]-hj, icen[1]+hj+1), axis=1)
        arr[i, jslc] = value

def box(dom, arr, value, point1, point2):
    '''
    Paint 3D box with value.
    '''
    point1 = dom.index(point1)
    point2 = dom.index(point2)

    s = [dom.crop(slice(point1[a], point2[a]), axis=a) for a in [0,1,2]]
    arr[tuple(s)] = value


def cylinder(dom, arr, value, radius, center, hheight, axis):
    '''
    Paint grid points of array with a value inside a 3D cylinder.

    Cylinder is described by its radius, center and half-height in
    spatial unit and the axis to which it is parallel.
    '''
    center = numpy.array(center)
    # we cheat and move the cylinder onto the grid
    icen = dom.index(center)

    n0 = int(floor(hheight/dom.spacing[axis]))
    slc0 = slice(icen[axis] - n0, icen[axis] + n0 +1)

    axis1 = (axis+1)%3          # march on this radius
    axis2 = (axis+2)%3          # fill on this secant

    # number of grid points on either of center along each axis
    irad = int(round(radius / dom.spacing[axis1]))

    # bounds of circle on axis1
    ibb = dom.crop(slice(icen[axis1]-irad, icen[axis1]+irad+1), axis=axis1)

    #... 0:axis1, 1:axis2, 
    for i in range(ibb.start, ibb.stop):
        ir = icen[axis1] - i
        h = radius**2 - (ir*dom.spacing[axis1])**2
        if h < 0:
            continue
        hj = int(floor(sqrt(h)/dom.spacing[axis2]))

        slc1 = dom.crop(slice(i,i+1), axis=axis1)

        # secant slice
        slc2 = dom.crop(slice(icen[axis2]-hj, icen[axis2]+hj+1), axis=axis2)

        slices = [None]*3
        slices[axis] = slc0
        slices[axis1] = slc1
        slices[axis2] = slc2
        arr[tuple(slices)] = value
