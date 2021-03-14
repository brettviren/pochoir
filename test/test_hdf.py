#!/usr/bin/env pytest
import os
import numpy
from pochoir import hdf 

def same(a1,a2):
    return (a1 == a2).all()

def test_various():
    fname = "test_hdf.hdf"      # fixme tempdir
    if os.path.exists(fname):
        os.unlink(fname)

    a = numpy.random.rand(100).reshape((-1,10))

    s = hdf.Store(fname, 'w')
    s.put("a", a)
    s2 = hdf.Store(fname, 'r')
    a2 = s2.get("a")
    assert same(a,a2)
    s.close()
    assert not hasattr(s, "fp")
    s2.close()
    s3 = hdf.Store(fname, 'a')
    assert s3.fp.mode in ('a','r+')
    s3.put("b",a)
    a3 = numpy.random.rand(400).reshape((-1,20))
    s3.put("a",a3, key1="val1")
    a3 = s3.get("a")
    print(dict(a3.attrs))
    assert a3.attrs['key1'] == "val1"
#    os.unlink(fname)
