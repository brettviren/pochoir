#!/usr/bin/env python3
'''
The pochoir problem domain.

'''

import numpy

from .arrays import fromstr1, gradient

class Domain:
    def __init__(self, shape, spacing, origin=None):
        '''
        Create a domain from individual arrays

        A domain describes by an N-d finite grid aligned with
        Cartesian coordinate axes.  For each dimension,

        coordinate = origin + index × spacing

        Where index refers to indices on some given array.

        '''
        self.shape = shape
        if isinstance(spacing, int) or isinstance(spacing,float):
            self.spacing = numpy.zeros(len(self.shape)) + spacing
        else:
            self.spacing = numpy.array(spacing)
        if origin is None:
            self.origin = numpy.zeros(len(self.shape), dtype=float)
        else:
            self.origin = numpy.array(origin)


    def point(self, index):
        '''
        Given the spatial point at the index.
        '''
        index = numpy.array(index)
        return self.origin + index * self.spacing


    def index(self, point):
        '''
        Given a point, return nearest index
        '''
        point = numpy.array(point)
        return numpy.array(numpy.round((point - self.origin)/self.spacing), dtype=int)


    def crop(self, slc, axis):
        '''
        Return slice slc possibly reduced to fit grid along axis
        '''
        s = slice(max(slc.start, 0),
                  min(slc.stop, self.shape[axis]))
        if s.start < s.stop:
            return s
        return slice(0,0)
            

    def imshow_extent(self, axis=None):
        '''
        Provide a 2D extent for plt.imshow().

        If axis is None, assume domain is 2D.

        Else, assume image is slicing perpendicular to axis

        [left, right, bottom, top] 
        '''
        if axis is None:
            if len(self.shape) != 2:
                raise ValueError("Must be 2D domain if not axis given")
            p1 = self.point((0,0))
            p2 = self.point((self.shape[0]-1, self.shape[1]-1))
            return (p1[0], p2[0], p2[1], p1[1])


        if len(self.shape) != 3:
            raise ValueError("Must be 3D domain if axis given")
        p1 = self.point((0,0,0))
        p2 = self.point([self.shape[i]-1 for i in [0,1,2]])
        axis1 = (axis + 1)%3
        axis2 = (axis + 2)%3
        return (p1[axis1], p2[axis1], p2[axis2], p1[axis2])


    @property
    def linspaces(self):
        '''
        Return vector of array, each giving the positions of grid
        points along a dimension of the domain.

        coordinate = origin + index × spacing
        '''
        ret = list()
        for num, sp, o in zip(self.shape, self.spacing, self.origin):
            first = o 
            last  = o + (num - 1) * sp
            ret.append(numpy.linspace(first, last, num))
        return ret
        
    @property
    def meshgrid(self):
        '''
        Return a meshgrid coresponding to the domain
        '''
        return numpy.meshgrid(*self.linspaces, indexing="ij")

    
    def gradient(self, scalar):
        '''
        Return the finite difference gradient of the scalar field.
        '''
        return gradient(scalar, self.spacing)


