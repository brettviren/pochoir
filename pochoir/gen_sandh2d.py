#!/usr/bin/env python3
'''
Generators of 2D strips-and-holes geometry (initial and boundary value
arrays).

This puts strips parallel to the spacial X-axis which is assumed to be
axis=1 in the array.  That is, a plane occupies a row of the array.
'''

from math import floor
import numpy
from .shapes import rectangle

# note: also see gen_sandh.gen_twod

def gradient(shape, v0, v1):
    '''
    Paint and dirty gradient on iarr.

    arr[0] has value v0 and arr[-1] has v1.
    '''
    print(f"painting gradient: {v0} -> {v1} for {shape}")
    g = numpy.linspace(v0, v1, shape[0], endpoint=False)
    arr = numpy.vstack([g]*shape[1]).T
    print(f"gradient shape: {arr.shape}")
    return arr


def generator(dom, cfg):
    '''
    Return iva/bva for sandh 2d

    '''
    planes = cfg['planes']
    isw = any([p.get("weighting", False) for p in planes])

    if not isw:
        planes.sort(key=lambda p: p['location'])
        cat_v = planes[-1]["voltage"]
        gnd_v = planes[0]["voltage"]
        grad = gradient(dom.shape, gnd_v, cat_v)

    #iarr = numpy.zeros(dom.shape)
    barr = numpy.zeros(dom.shape, dtype=bool)
    iarr = numpy.zeros(dom.shape, dtype="float32")
    
    bb = dom.bb
    halfwidth = 0.5*(bb[1][1] - bb[0][1])

    clx = numpy.array(cfg['centerline'])

    def rect(p1, p2, val, mask):
        rectangle(dom, iarr,  val, p1, p2)
        rectangle(dom, barr, mask, p1, p2)


    for plane in planes:
        def locit(what):
            return round(plane[what]/dom.spacing[0])*dom.spacing[0]

        name = plane['name']
        pitch = plane['pitch']
        thick = plane['thick']
        diam = plane.get('diameter', None)
        gap = plane['gap']
        loc = locit('location') # in Y
        print(f'{name}: {loc}')
        pot = plane['voltage']  # bias V or 1.0/0.0 if isw
        isw = plane['weighting'] # is weighting bool

        # half-wid of a strip
        shalfwid = 0.5*(pitch-gap)

        # number of strips on one side of strip0
        nstrips = int(floor(halfwidth/pitch))

        # "draw" each strip
        for istrip in range(-nstrips, nstrips+1):

            val = pot
            if istrip and isw:
                val = 0.0

            # strip center line origin
            scl = numpy.array([loc, istrip * pitch - clx])

            edge = numpy.array([0.5*thick, shalfwid])
            p1 = scl - edge
            p2 = scl + edge
            rect(p1, p2, val, True)

            print(f'{name}: s#{istrip}({isw}) p={pitch} scl={scl} val={val} on {p1} -> {p2}')
            if not diam:
                continue

            hole = numpy.array([0.5*thick, 0.5*diam])
            p1 = scl - hole
            p2 = scl + hole
            # "erase" hole
            rect(p1, p2, 0, False)

    print('GEN ssandh2d totals:',numpy.sum(iarr), numpy.sum(barr))
    print('GEN bb:',bb)
    if not isw:
        notbarr = numpy.invert(barr)
        iarr = iarr + notbarr*grad

    return iarr, barr
