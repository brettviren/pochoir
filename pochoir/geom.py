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
        value = values.get(name, default)
        #print (f'{st} {name} {value}')
        meth(dom, arr, value, **shape)

def init(dom, cfg, ambient=0.0):
    '''
    Create initial and boundary value arrays.
    '''
    ndim = len(dom.shape)
    known = pochoir.shapes.known(ndim)
    shapes = cfg['shapes']

    # pre-check sanity
    for shape in shapes:
        name = shape['name']
        st = shape['type']
        if st not in known:
            raise ValueError(f'shape {name} unsupported {ndim}-D type {st}')

    values = cfg['values']

    bvalues = {k:True for k in values}
    
    #print ("BOUNDARY")
    barr = numpy.zeros(dom.shape, dtype=bool)
    render(dom, barr, shapes, bvalues, False)

    #print ("INITIAL")
    iarr = numpy.zeros(dom.shape, dtype='f4') + ambient
    render(dom, iarr, shapes, values, ambient)

    return iarr, barr
