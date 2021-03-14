#!/usr/bin/env pytest

from pochoir.util import flatten

def test_flatten():
    d = dict(a=dict(b=dict(c=42, a="different a"), c=6.9), l=[1,2])
    print(f'before: {d}')
    d = flatten(d, "|sep|", "PARENT:")
    print(f'after: {d}')
    for k,v in d.items():
        assert k.startswith("PARENT:")
        assert not isinstance(v, dict)
