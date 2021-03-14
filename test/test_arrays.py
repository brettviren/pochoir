import numpy
from pochoir.arrays import core1, pad1

def test_core1():
    a = numpy.array(range(12)).reshape((3,4))
    c = core1(a)
    assert c.shape == (1,2)
    assert c[0][0] == 5
    assert c[0][1] == 6


def test_pad1():
    a = numpy.array(range(12)).reshape((3,4))
    p = pad1(a)
    assert p.shape == (5,6)
    assert 0 == numpy.sum(p[:,0])
    assert 0 == numpy.sum(p[0,:])
    assert 0 == numpy.sum(p[:,-1])
    assert 0 == numpy.sum(p[-1,:])
    assert (p[1:-1,1:-1] == a).all()
    
