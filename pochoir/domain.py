#!/usr/bin/env python3
'''
The pochoir problem domain.

A domain is an N-d finite grid aligned with Cartesian coordinate axes.  
'''
from .arrays import fromstr1, ones, zeros, linspace, meshgrid

class Domain:
    def __init__(self, shape, spacing, origin=None, first=None):
        '''
        Create a domain from individual arrays
        '''
        self.shape = shape
        self.spacing = spacing
        if origin is None:
            self.origin = zeros(shape.size, dtype=float)
        else:
            self.origin = origin
        if first is None:
            self.first = zeros(shape.size, dtype=int)
        else:
            self.first = first

    @property
    def imshow_extent(self):
        '''
        If this domain is 2D it can have an extent suitable for
        passing to plt.imshow()

        [left, right, bottom, top] 
        '''
        if self.shape.size != 2:
            raise ValueError("Must be 2D domain")
        b = list()
        for num, sp, o, f in zip(self.shape, self.spacing, self.origin, self.first):
            first = o + f * sp
            last  = o + (f + num - 1) * sp
            b.append((first,last))
        return [b[0][0], b[0][1], b[1][1], b[1][0]]

    @property
    def linspaces(self):
        '''
        Return vector of array, each giving the positions of grid
        points along a dimension of the domain.

        coordinate = origin + index × spacing
        '''
        ret = list()
        for num, sp, o, f in zip(self.shape, self.spacing, self.origin, self.first):
            first = o + f * sp
            last  = o + (f + num - 1) * sp
            ret.append(linspace(first, last, num))
        return ret
        
    @property
    def meshgrid(self):
        '''
        Return a meshgrid coresponding to the domain
        '''
        return meshgrid(*self.linspaces, indexing="ij")

    
        
