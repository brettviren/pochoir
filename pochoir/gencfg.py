#!/usr/bin/env python3

import os
import json

def loadf(filename):
    '''
    Load a file interpreting extention as format.  
    
    Return data structure.
    '''
    # Note, the local imports here are intentional to avoid triggering
    # dependency if user eschews one or the other module.

    if filename.endswith(".jsonnet"):
        from .jsonnet import load
        return load(filename)
    else:
        import anyconfig
        return anyconfig.load(filename)

def dump(data):
    '''
    Return data as unencoded JSON string.
    '''
    return json.dumps(data, indent=4)

def multi(filename, outdir):
    '''
    Load named file and interpret keys as file names relative to
    outdir, writing each subobject as a file.

    This will first generate into a temporary directory and will only
    overwrite file contents if they differ.
    '''

    data = loadf(filename)
    for fname, fdata in data.items():
        path = os.path.realpath(os.path.join(outdir, fname))
        pdir = os.path.dirname(path)
        if not os.path.exists(pdir):
            os.makedirs(pdir)
        if os.path.exists(path): # only overwrite if content changes
            oldtext = open(path, 'rb').read().decode()
            newtext = dump(fdata)
            if newtext == oldtext:
                print (f'old: {path}')
                continue

        with open(os.path.join(outdir, path), "wb") as fp:
            print (f'new: {path}')
            fp.write(dump(fdata).encode())
            
    
    
