#!/usr/bin/env pytest

import os
import numpy
from pochoir import npz
import pytest
from pathlib import Path

def test_putget():
    test_base = "/tmp/test_npz"
    s1 = npz.Store(test_base,"r")
    with pytest.raises(OSError) as oe:
        s1.put("should-fail", list())
    s2 = npz.Store(test_base, "a")
    s2.put("empty", [], foo="bar", baz=42)
    assert os.path.exists(test_base + '/empty.npz')
    assert os.path.exists(test_base + '/empty.json')

    s3 = npz.Store(test_base, "r")
    ds, md = s3.get("empty", True)
    assert md['foo'] == 'bar'
    assert md['baz'] == 42
    
