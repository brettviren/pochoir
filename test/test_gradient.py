#!/usr/bin/env pytest

import numpy
import pochoir

def test_gradient():

    lin = numpy.arange(0,10,1)
    pot = numpy.vstack([lin,lin,lin,lin])
    g = pochoir.arrays.gradient(pot)
    assert numpy.all(g[0] == 0)
    assert numpy.all(g[1] == 1)    
