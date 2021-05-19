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

def assure_parent(filepath):
    path = os.path.realpath(filepath)
    pdir = os.path.dirname(path)
    if not os.path.exists(pdir):
        os.makedirs(pdir)
    return path
    

def multi(filename, outdir, listing=None):
    '''
    Load named file and interpret keys as file names relative to
    outdir, writing each subobject as a file.

    A file is only made anew if its contents would differ.

    If listing is given, write file names, one per line.
    '''

    data = loadf(filename)
    for fname, fdata in data.items():
        path = assure_parent(os.path.join(outdir, fname))

        if os.path.exists(path): # only overwrite if content changes
            oldtext = open(path, 'rb').read().decode()
            newtext = dump(fdata)
            if newtext == oldtext:
                print (f'old: {path}')
                continue
            print (f'bad: {path}')

        with open(os.path.join(outdir, path), "wb") as fp:
            print (f'new: {path}')
            fp.write(dump(fdata).encode())

    if listing is None:
        return

    listing = assure_parent(listing)
    lines = list(sorted(data))
    with open(listing, "wb") as fp:
        text = '\n'.join(lines)
        text += '\n'
        fp.write(text.encode())
        
    
