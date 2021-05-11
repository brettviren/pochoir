import numpy
from pochoir.domain import Domain
from pochoir.plots import quiver

def test_quiver_3d():
    d = Domain([20,10,100], [0.1, 0.1, 0.1])
    assert (d.shape == (20,10,100)).all()
    assert (d.shape.size == 3)
    assert (d.spacing.size == 3)
    assert (d.origin.size == 3)
    lss = d.linspaces
    for ls,size in zip(lss, d.shape):
        assert(len(ls) == size)

    print(d.shape)
    scalar = numpy.random.rand(*d.shape)
    print(scalar.shape)
    vector = numpy.gradient(scalar)
    print(vector[0].shape)
    quiver(vector, "test_quiver_3d.png", d)


def test_quiver_2d():
    d = Domain([20,10], [0.1, 0.1], [200.0, 100.0])
    assert (d.shape == (20,10)).all()
    lss = d.linspaces
    for ls,size in zip(lss, d.shape):
        assert(len(ls) == size)
    print (d.imshow_extent)

    scalar = numpy.random.rand(*d.shape)
    vector = numpy.gradient(scalar)
    quiver(vector, "test_quiver_2d.png", d)
