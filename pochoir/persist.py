#!/usr/bin/env python3
'''
Generic interface to persistent storage.

A "block" here means a Numpy-like object with a name.  The name is
used to locate the block in a persistent store.
'''

from . import hdf
from . import npz

def store(filename, mode="a", fmt=None):
    '''
    Return a store of a certain format.

    If mode may be 'r' (readonly), 'w' (recreate), or 'a' (update).
    '''
    if fmt is None:
        if ".hdf" in filename:
            fmt = "hdf"
        else:
            fmt = "npz"
    if 'hdf' in fmt:
        return hdf.Store(filename, mode)
    if 'npz' in fmt:
        return npz.Store(filename, mode)
    raise ValueError(f'unsupported file fromat {fmt}')
    
