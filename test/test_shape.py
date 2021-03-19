#!/usr/bin/env python3

import numpy
import matplotlib.pyplot as plt

from pochoir.shapes import cylinder, circle2d

def test_circle2d():
    shape=(50,50)
    arr = numpy.zeros(shape)

    radius=23
    center=(25,25)

    circle2d(arr, radius, center, 1.0)

    arr = numpy.ma.masked_array(arr, arr >= 100)
    plt.imshow(arr, interpolation='none', aspect='equal')
    plt.colorbar()
    plt.savefig("test_circle.pdf")
    

def test_cylinder():
    arr = numpy.zeros((50,50,50))
    cylinder(arr, 20, (25,25,25), 20, 0, 1)

    fig, axes = plt.subplots(1,3)
    axes[0].imshow(arr[25,:,:], interpolation='none', aspect='equal')
    axes[1].imshow(arr[:,25,:], interpolation='none', aspect='equal')
    axes[2].imshow(arr[:,:,25], interpolation='none', aspect='equal')
    fig.savefig("test_cylinder.pdf")
    
