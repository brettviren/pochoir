#!/usr/bin/env pytest

import os

import numpy
from pochoir import npz
import pytest
from pathlib import Path

from shutil import rmtree
from tempfile import mkdtemp


def test_putget():
    store_dir = mkdtemp(prefix="test-npz-putget")
    s1 = npz.Store(store_dir,"r")
    with pytest.raises(OSError) as oe:
        s1.put("should-fail", list())
    s2 = npz.Store(store_dir, "a")
    s2.put("empty", [], foo="bar", baz=42)
    assert os.path.exists(store_dir + '/empty.npz')
    assert os.path.exists(store_dir + '/empty.json')

    s3 = npz.Store(store_dir, "r")
    ds, md = s3.get("empty", True)
    assert md['foo'] == 'bar'
    assert md['baz'] == 42
    rmtree(store_dir)
    
