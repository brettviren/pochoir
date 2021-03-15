#!/usr/bin/env python3

import numpy
from pochoir.shapes import *

def test_sphere():
    c = [0,0]
    s2 = Sphere(1, c)
    assert s2.inside(c)
    assert s2.inside([0.5,0.5])
    assert s2.inside([1.0,0])
    assert s2.inside([0,1.0])
    assert not s2.inside([1,1])

    c = [0,0,0]
    s3 = Sphere(1, c)
    assert s3.inside(c)
    assert s3.inside([0.5, 0.5, 0.5])
    assert s3.inside([1.0, 0.0, 0.0])
    assert s3.inside([0.0, 1.0, 0.0])
    assert not s3.inside([1, 1, 0])
    

def test_shelf():
    ends = ([1,2,3], [10,20,30])
    s = Shelf(*ends)
    assert s.inside(ends[0])
    assert s.inside(ends[1])
    assert s.inside([1,2,3])
    assert s.inside([5,15,25])
    assert not s.inside([0,0,0])


def test_cylinder():
    ends = ([-1,-2,-3], [1,2,3])
    s = Cylinder(1, *ends)
    assert s.inside([0,0,0])
    assert s.inside(ends[0])
    assert s.inside(ends[1])
    assert not s.inside([1.5, 0, 0])

def test_boolean():
    ends = ([-100,-10,1], [100,10,1])
    s = Shelf(*ends)
    b = Sphere(2, [0,0,0])
    u = Union(s,b)
    assert u.inside([0,0,2])

    i = Intersection(s,b)
    assert not i.inside([0,0,2])
    assert not i.inside([10,0,0])    

    h = Hole(b)
    sh = Intersection(s, h)
    assert not sh.inside([0,0,0])
    
