import numpy
from pochoir.arrays import core1, pad1, fromstr1

def test_fromstr1():

    fff = fromstr1("15 * cm, 150, 150*mm, 150.0", float)
    assert all([f==150.0 for f in fff])
    iii = fromstr1("15 * cm, 150, 150*mm, 150.0", int)
    assert all([i==150 for i in iii])

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
    
