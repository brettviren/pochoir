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

def generator(dom, cfg):
    '''
    Return iva/bva for sandh 2d

    '''

    iarr = numpy.zeros(dom.shape)
    barr = numpy.zeros(dom.shape, dtype=bool)
    
    bb = dom.bb
    halfwidth = 0.5*(bb[1][1] - bb[0][1])

    clx = numpy.array(cfg['centerline'])

    def rect(p1, p2, val, mask):
        rectangle(dom, iarr,  val, p1, p2)
        rectangle(dom, barr, mask, p1, p2)

    for plane in cfg['planes']:
        name = plane['name']
        pitch = plane['pitch']
        thick = plane['thick']
        diam = plane.get('diameter', None)
        gap = plane['gap']
        loc = plane['location'] # in Y
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
    return iarr, barr
