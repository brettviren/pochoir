#!/usr/bin/env python3
'''
Utility functions
'''

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
