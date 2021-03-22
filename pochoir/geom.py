#!/usr/bin/env python3
'''
Functions related to spatial geometry.
'''
import numpy
import pochoir.shapes

def render(dom, arr, shapes, values, default):
    '''
    Render shapes onto array
    '''
    for shape in shapes:
        shape = dict(shape)
        name = shape.pop('name')
        st = shape.pop('type')
        meth = getattr(pochoir.shapes, st)
        value = values.get('name', False)
        meth(dom, arr, value, **shape)

def init(dom, cfg, ambient=0.0):
    '''
    Create initial and boundary value arrays.
    '''
    ndim = len(dom.shape)
    known = pochoir.shapes.known(ndim)
    shapes = cfg['shapes']
    for shape in shapes:
        name = shape['name']
        st = shape['type']
        if st not in known:
            raise ValueError(f'shape {name} unsupported {ndim}-D type {st}')

    values = cfg['values']

    barr = numpy.zeros(dom.shape, dtype=bool)
    render(dom, barr, shapes, values, False)

    iarr = numpy.zeros(dom.shape, dtype='f4') + ambient
    render(dom, barr, shapes, values, ambient)

    return iarr, barr
