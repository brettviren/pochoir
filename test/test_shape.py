#!/usr/bin/env python3

import numpy
import matplotlib.pyplot as plt

from pochoir.shapes import cylinder, circle, box, rectangle
from pochoir.domain import Domain



def test_circle():
    dom = Domain(shape=(100,100), spacing=0.1)

    arr = numpy.zeros(dom.shape)

    circle(dom, arr,          1.0, 2.0, (0,0))
    circle(dom, arr,          1.0, 2.0, (10,10))
    circle(dom, arr,          1.0, 2.0, (0,10))
    circle(dom, arr,          1.0, 2.0, (10,0))

    circle(dom, arr,         -1.0, 2.3, (-2.5, -2.5))
    circle(dom, arr,         -1.0, 2.0, (-1.0,-1.0))
    circle(dom, arr,         -2.0, 2.0, (-1.0, 6.0))
    circle(dom, arr,         -3.0, 2.0, ( 6.0, 6.0))
    circle(dom, arr,       1000.0, 2.0, (160,160))
    
    plot2(dom, arr, "test_circle.pdf")
    

def test_rectangle():
    dom = Domain(shape=(100,100), spacing=0.1)
    arr = numpy.zeros(dom.shape)

    rectangle(dom, arr, 1, (-1.0,2.5), (1.0,3.5))
    rectangle(dom, arr, 2, (2.0,-1.0), (3.0,2.7))
    rectangle(dom, arr, 3, (4.0,4.0), (6.0,6.0))
    rectangle(dom, arr, 4, (2.5,2.5), (3.5,3.5))

    plot2(dom, arr, "test_rectangle.pdf")


def test_holes2d():
    dom = Domain(shape=(100,100), spacing=0.1)
    arr = numpy.zeros(dom.shape)

    for s in range(3):
        c = s*5
        rectangle(dom, arr, s+1, (c-2,0), (c+2,10))
    for s in range(0,3,2):
        c = s*5
        circle(dom, arr, -(s+1), 2, (c-2.5, 0))
        circle(dom, arr, -(s+1), 2, (c-2.5, 10))
    for s in range(1,4,2):
        c = s*5
        circle(dom, arr, -(s+1), 2, (c-2.5, 5))

    plot2(dom, arr, "test_holes2d.pdf")

def plot2(dom, arr, fname, dead=0):
    arr = numpy.ma.masked_array(arr, arr == dead)
    plt.imshow(arr, interpolation='none', aspect='equal',
               extent = dom.imshow_extent())
    plt.colorbar()
    plt.savefig(fname)


def plot3(dom, arr, center, filename, dead=0):
    fig, axes = plt.subplots(1,3)
    c0,c1,c2 = dom.index(center)

    arr = numpy.ma.masked_array(arr, arr == dead)

    axes[0].set_title('axis=0')
    axes[0].imshow(arr[c0,:,:], interpolation='none', aspect='equal',
               extent = dom.imshow_extent(0))
    axes[1].set_title('axis=1')
    axes[1].imshow(arr[:,c1,:], interpolation='none', aspect='equal',
                   extent = dom.imshow_extent(1))
    axes[2].set_title('axis=2')
    axes[2].imshow(arr[:,:,c2], interpolation='none', aspect='equal',
                   extent = dom.imshow_extent(2))
    fig.savefig(filename)
    

def test_cylinder():
    dom = Domain(shape=(100,100,100), spacing=0.1)
    arr = numpy.zeros(dom.shape)

    cylinder(dom, arr, 1, 4, (3,4,5), 2, 0)
    plot3(dom, arr, (5,5,5), "test_cylinder.pdf")

    # fig, axes = plt.subplots(1,3)
    # axes[0].imshow(arr[25,:,:], interpolation='none', aspect='equal')
    # axes[1].imshow(arr[:,25,:], interpolation='none', aspect='equal')
    # axes[2].imshow(arr[:,:,25], interpolation='none', aspect='equal')
    # fig.savefig("test_cylinder.pdf")
    

def test_box3d():
    '''
    simplest thing to specify box in real coords
    '''
    dom = Domain(shape=(100,100,100), spacing=0.1)
    arr = numpy.zeros(dom.shape)

    # in same units as spacing and origin
    ends = [(2,3,4), (9,8,7)]
    box(dom, arr, 1.0, *ends)
    plot3(dom, arr, (5,5,5), "test_box3d.pdf")
    
