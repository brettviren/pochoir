#!/usr/bin/env python3
'''
Utility functions
'''

from pochoir import units
import collections

def flatten(d, sep='/', parent_key=""):
    '''
    Flatten a hierarchical dict-like object.

    Return dict with keys reflecting hiearchy with given delimieter
    '''
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        try:
            
            items.extend(flatten(v, sep, new_key).items())
        except AttributeError:
            items.append((new_key, v))
    return dict(items)

def unitify(dat):
    '''
    Apply units to things that look like they need it.

    This does an eval, so trust your dat.
    '''
    if isinstance(dat, str):
        dat = dat.strip()
        if "*" in dat:          
            try:
                return eval(dat, units.__dict__)
            except Exception:
                return dat
        return dat
    if isinstance(dat, list):
        return [unitify(d) for d in dat]
    if isinstance(dat, dict):
        return {k:unitify(v) for k,v in dat.items()}
    return dat
