#!/usr/bin/env python3
'''
Export pochoir data to vtk files
'''

from .arrays import to_numpy

from pyevtk.hl import gridToVTK, imageToVTK

def image3d(name, **scalars):
    '''
    Export scalar field to vtk image file of name.
    '''
    scalars = {k:to_numpy(v) for k,v in scalars.items()}
    imageToVTK(name, pointData=scalars)
