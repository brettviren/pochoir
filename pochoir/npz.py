#!/usr/bin/env python3
'''
pochoir support for NPZ file format

This mimics HDF5 model.
'''

import os
import json
import numpy
from pathlib import Path

class Store:

    dsext = ".npz"
    mdext = ".json"

    def __init__(self, basedir, mode):
        '''
        Create a NPZ+JSON store rooted on basedir.
        '''
        self.basedir = Path(basedir)
        if not self.basedir.exists():
            self.basedir.mkdir(parents=True)
        self.mode = mode

    def dspath(self, key):
        if key in ["",".","/"]:
            return self.basedir
        maybe_dir = self.basedir.joinpath(key)
        if maybe_dir.is_dir():
            return maybe_dir
        return self.basedir.joinpath(key + self.dsext)

    def get(self, key, metadata=False):
        '''
        Get dataset and maybe metadata with key relative to store.
        '''
        dp = self.dspath(key)
        if dp.is_dir():
            return (tuple([f.stem for f in dp.glob("*") if f.is_dir()]),
                    tuple([f.stem for f in dp.glob("*"+self.dsext)]),
                    tuple([f.stem for f in dp.glob("*"+self.mdext)]))

        arr = None
        md = None
        npz = dp.parent.joinpath(dp.stem + self.dsext)
        if npz.exists():
            arrs = numpy.load(dp.resolve())
            arr = arrs[dp.stem]
        mdf = dp.parent.joinpath(dp.stem + self.mdext)
        if mdf.exists():
            md = dict()
            if mdf.exists():
                md = json.loads(open(mdf.resolve(),'rb').read().decode())
        if metadata:
            return arr, md
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
    

