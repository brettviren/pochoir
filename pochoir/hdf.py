#!/usr/bin/env python3
'''
pochoir support for HDF5 file format
'''

import h5py
from .util import flatten


# we put a thin wrapper around h5py.File to keep open npz or other formats
class Store:

    def __init__(self, filename, mode):
        self.fp = h5py.File(filename, mode)

    def get(self, key, metadata=False):
        ds = self.fp[key]
        if metadata:
            return (ds, ds.attrs)
        return ds

    def put(self, key, value, **attrs):
        if self.fp.mode in ('a', 'r+') and key in self.fp:
            self.fp.pop(key)
        self.fp[key] = value
        self.fp[key].attrs.update(attrs)

    def close(self):
        self.fp.close()
        del self.fp
