#!/usr/bin/env python3
'''
Generic interface to persistent storage.

A "block" here means a Numpy-like object with a name.  The name is
used to locate the block in a persistent store.
'''

from . import hdf
from . import npz

def backend(filename, fmt=None):
    if fmt is None:
        if ".hdf" in filename:
            fmt = "hdf"
        else:
            fmt = "npz"
    return fmt

def store(filename, mode="a", fmt=None):
    '''
    Return a store of a certain format.

    If mode may be 'r' (readonly), 'w' (recreate), or 'a' (update).
    '''
    fmt = backend(filename, fmt)
    if 'hdf' in fmt:
        return hdf.Store(filename, mode)
    if 'npz' in fmt:
        return npz.Store(filename, mode)
    raise ValueError(f'unsupported file fromat {fmt}')
    

import os
from shutil import rmtree
from tempfile import mkdtemp
from contextlib import contextmanager

@contextmanager
def tempstore(prefix="pochoir-store", fmt='npz'):
    if 'hdf' in fmt:
        fd, fname = mkstemp(suffix='.hdf', prefix=prefix)
        os.close(fd)
        store = hdf.Store(fname, 'a')
    elif 'npz' in fmt:
        fname = mkdtemp(prefix=prefix)
        store = npz.Store(fname, 'a')
    else:
        raise ValueError(f'Unknown store format: {fmt}')
    print(f'tempstore({prefix},{fmt}) -> {fname}') 

    try:
        yield store
    finally:
        if 'hdf' in fmt:
            os.unlink(fname)
        else:
            rmtree(fname)
