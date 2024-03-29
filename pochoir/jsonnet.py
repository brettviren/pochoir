#!/usr/bin/env python3

# This comes from moo.

import os
import json
from _jsonnet import evaluate_file, evaluate_snippet
# from moo.util import clean_paths, resolve
def clean_paths(paths, add_cwd=True):
    '''Return list of paths made absolute with cwd as first .

    Input "paths" may be a ":"-separated string or list of string.

    If add_cwd is True and if cwd is not already in paths, it will be
    prepended.

    '''
    if isinstance(paths, str):
        paths = paths.split(":")
    paths = [os.path.realpath(p) for p in paths]

    if add_cwd:
        cwd = os.path.realpath(os.path.curdir)
        if cwd not in paths:
            paths.insert(0, cwd)

    return paths

def resolve(filename, paths=()):
    '''Resolve filename'''
    if not filename:
        raise ValueError("no file name provided")
    if filename.startswith('/'):
        return filename

    for maybe in clean_paths(paths):
        fp = os.path.join(maybe, filename)
        if os.path.exists(fp):
            return fp
    raise ValueError(f"file not found: {filename}")

def try_path(path, rel):
    '''
    Try to open a path
    '''
    if not rel:
        raise RuntimeError('Got invalid filename (empty string).')
    if rel[0] == '/':
        full_path = rel
    else:
        full_path = os.path.join(path, rel)
    if full_path[-1] == '/':
        raise RuntimeError('Attempted to import a directory')

    if not os.path.isfile(full_path):
        return full_path, None
    with open(full_path) as f:
        return full_path, f.read()


class ImportCallback(object):

    def __init__(self, paths=()):
        self.paths = list(paths) + [
            os.path.join(os.path.dirname(__file__),
                         "jsonnet-code")]
        self.found = set()

    def __call__(self, path, rel):
        paths = [path] + self.paths
        for maybe in paths:
            try:
                full_path, content = try_path(maybe, rel)
            except RuntimeError:
                continue
            if content:
                self.found.add(full_path)
                return full_path, content
        raise RuntimeError('File not found')


def load(fname, paths=(), **kwds):
    '''
    Load a Jsonnet file.

    some useful kwds are:

    - ext_vars :: dictionary of variables, to get via std.extVar()
    - ext_codes :: dictionary of code, to get via std.extVar()
    - native_callbacks :: call python from Jsonnet
    - import_callbacks ::  help find imports

    '''
    paths = clean_paths(paths)
    fname = resolve(fname, paths)
    ic = ImportCallback(paths)
    try:
        text = evaluate_file(fname, import_callback=ic, **kwds)
    except RuntimeError as err:
        raise RuntimeError(f"in file: {fname}") from err
    return json.loads(text)


def loads(jtext, paths=(), **kwds):
    '''
    Load Jsonnet text
    '''
    paths = clean_paths(paths)
    ic = ImportCallback(paths)
    text = evaluate_snippet("<stdin>", jtext, import_callback=ic, **kwds)
    return json.loads(text)


def imports(fname, paths=(), **kwds):
    '''
    Return the imports needed by the Jsonnet file
    '''
    paths = clean_paths(paths)
    fname = resolve(fname, paths)
    ic = ImportCallback(paths)
    evaluate_file(fname, import_callback=ic, **kwds)
    ret = list(ic.found)
    ret.sort()
    return ret

