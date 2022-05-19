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
    if 'npz' in fmt or 'json' in fmt:
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

from .schema import FieldResponse, PlaneResponse, PathResponse
import json

def todict(obj):
    '''
    Return a dictionary for the object which is marked up for type.
    '''
    for typename in ['FieldResponse', 'PlaneResponse', 'PathResponse']:
        if typename == type(obj).__name__:
            cname = obj.__class__.__name__
            return {cname: {k: todict(v) for k, v in obj._asdict().items()}}
    if isinstance(obj, numpy.ndarray):
        shape = list(obj.shape)
        elements = obj.flatten().tolist()
        return dict(array=dict(shape=shape, elements=elements))
    if isinstance(obj, list):
        return [todict(ele) for ele in obj]

    return obj


def fromdict(obj):
    '''
    Undo `todict()`.
    '''
    if isinstance(obj, dict):

        if 'array' in obj:
            ret = numpy.asarray(obj['array']['elements'])
            return ret.reshape(obj['array']['shape'])

        for typ in [FieldResponse, PlaneResponse, PathResponse]:
            tname = typ.__name__
            if tname in obj:
                return typ(**{k: fromdict(v) for k, v in obj[tname].items() if k not in ["pitchdir","wiredir"]})

    if isinstance(obj, list):
        return [fromdict(ele) for ele in obj]

    return obj


def dumps(obj):
    '''
    Dump object to JSON text.
    '''
    return json.dumps(todict(obj), indent=2)


def loads(text):
    '''
    Load object from JSON text.
    '''
    return fromdict(json.loads(text))


def dumpfr(filename, obj):
    '''
    Save a response object (typically response.schema.FieldResponse)
    to a file of the given name.
    '''
    text = dumps(obj)
    if filename.endswith(".json"):
        open(filename, 'w').write(text)
        return
    if filename.endswith(".json.bz2"):
        import bz2
        bz2.BZ2File(filename, 'wb').write(text.encode())
        return
    if filename.endswith(".json.gz"):
        import gzip
        gzip.open(filename, "wb").write(text.encode())
        return
    raise ValueError("unknown file format: %s" % filename)
