#!/usr/bin/env python3
'''
Shape grid "painting" functions.

These functions set grid points to values.  Functions are called in
terms of grid indicies (eg center) and any distance is in units of the
grid spacing.

Something else must translate from spatial dimensions to indicies, if
that is required.
'''
from math import sqrt, floor


def cylinder(arr, radius, center, hheight, axis, value):
    '''
    Paint grid points of array with value in shape of 3D cylinder.

    - radius gives cylinder radius in units of grid separation
    - center is the N-d grid indicies of the center of the cylinder
    - hheight is the half height in units of grid separation
    - axis is the parallel to the cylinder axis
    - value is the value to paint
    '''

    r2 = radius*radius

    #positions along axis
    c0 = center[axis]
    top = center[axis] + hheight
    bot = center[axis] - hheight
    along = slice(bot,top+1)

    axis1 = (axis+1)%3
    axis2 = (axis+2)%3

    c1 = center[axis1]
    c2 = center[axis2]

    for i in range(radius+1):
        rho = int(floor(sqrt(r2-i*i)))
        across = slice(c1-rho, c1+rho+1)
        atp = slice(c2+i,c2+i+1)
        atm = slice(c2-i,c2-i+1)

        sl = [None]*3
        sl[axis] = along
        sl[axis1] = across
        sl[axis2] = atp
        arr[tuple(sl)] = value
        sl[axis2] = atm
        arr[tuple(sl)] = value
        
def box(arr, ends, value):
    '''
    Paint 3D box with value.
    '''
    e1,e2 = ends
    arr[e1[0]:e2[0], e1[1]+1,e2[1]+1, e1[2]:e2[2]+1] = value

def rectangle2d(arr, ends, value):
    '''
    Paint grid points in a rectangle with end points, inclusive.
    '''
    e1,e2 = ends
    arr[e1[0]:e2[0], e1[1]+1,e2[1]+1] = value


def circle2d(arr, radius, center, value):
    '''
    Paint gridpoints withing a 2D circle of radius and center with value.
    '''

    r2 = radius*radius
    ci,cj = center
    for i in range(radius+1):
        h = int(floor(sqrt(r2-i*i)))
        arr[ci+i, cj-h:cj+h+1] = value
        arr[ci-i, cj-h:cj+h+1] = value
