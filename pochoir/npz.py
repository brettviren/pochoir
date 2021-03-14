#!/usr/bin/env python3
'''
pochoir support for NPZ file format

This mimics HDF5 model in the following way:

- a dataset is an array held in an .npz file.  
- a dataset name is reflected in both the .npz file and the array key.
- a group is a file system directory
- metadata on dataset or group is held in a JSON file of the same name

'''

import os
import json
import numpy
from pathlib import Path

class Store:

    dsext = ".npz"
    mdext = ".json"

    def __init__(self, basedir, mode):
        self.basedir = Path(basedir)
        if not self.basedir.exists():
            self.basedir.mkdir(parents=True)
        self.mode = mode

    def dspath(self, key):
        return self.basedir.joinpath(key + self.dsext)

    def get(self, key, metadata=False):
        dp = self.dspath(key)
        if not dp.exists():
            raise KeyError(f'no data set at {dp.resolve()}')
        arrs = numpy.load(dp.resolve())
        arr = arrs[key]
        if metadata:
            mdpath = dp.parent.joinpath(dp.stem + self.mdext)
            md = dict()
            if mdpath.exists():
                md = json.loads(open(mdpath.resolve(),'rb').read().decode())
            return (arr, md)
        return arr

    def put(self, key, value, **attrs):
        if self.mode == 'r':
            raise OSError("Unable to create link (read only)")

        dp = self.dspath(key)
        if dp.exists():
            if self.mode in ('a', 'r+'):
                dp.unlink()
            else:
                raise OSError("Unable to create link (name already exists)")
        elif not dp.parent.exists():
            dp.parent.mkdir(parents=True)
        name = dp.stem
        arrs = {name:value}
        numpy.savez(dp.resolve(), **arrs)
        if attrs:
            mp = dp.parent.joinpath(name + self.mdext)
            open(mp.resolve(), 'w').write(json.dumps(attrs, indent=4))

    def close(self):
        self.fp.close()
        del self.fp


def dump(filename, **blocks):
    '''
    Save blocks to named file.
    '''
    numpy.savez(filename, **blocks)


def load1(filename, key):
    '''
    Return array in named file at key
    '''
    fp = numpy.load(filename)
    return fp[key]
    

def load(filename):
    '''
    Return dict of all arrays in named file
    '''
    return numpy.load(filename)
    

