#!/usr/bin/env python
'''
Solid shapes.

Every shape has an inside() method returning Boolean.
'''

import math
import numpy



class Sphere:

    def __init__(self, radius, center):
        self.center = numpy.array(center)
        self.radius2 = radius*radius

    def inside(self, point):
        point = numpy.array(point)
        d = point - self.center
        return numpy.dot(d,d) <= self.radius2


class Shelf:
    'A box aligned with coordinates'

    def __init__(self, p1, p2):
        self.ends = (numpy.array(p1), numpy.array(p2))

    def inside(self, point):
        p = numpy.array(point)
        p1,p2 = self.ends
        return (p1 <= p).all() and (p <= p2).all()


class Cylinder:

    def __init__(self, radius, p1, p2):
        self.ends = (numpy.array(p1), numpy.array(p2))
        diff = self.ends[1] - self.ends[0]
        self.dist = math.sqrt(numpy.dot(diff, diff))
        self.rel = diff / self.dist
        self.radius2 = radius*radius

    def inside(self, point):
        point = numpy.array(point)
        diff = point - self.ends[0]
        along = numpy.dot(diff, self.rel)
        if along < 0 or along > self.dist:
            return False
        return numpy.dot(diff,diff) - numpy.dot(along,along) <= self.radius2
        

class Union:
    def __init__(self, *shapes):
        self.shapes = shapes
    def inside(self, point):
        return any([s.inside(point) for s in self.shapes])


class Intersection:
    def __init__(self, *shapes):
        self.shapes = shapes
    def inside(self, point):
        return all([s.inside(point) for s in self.shapes])


class Hole:
    'An inside-out shape'
    def __init__(self, shape):
        self.shape = shape
    def inside(self, point):
        return not self.shape.inside(point)
