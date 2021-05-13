#!/usr/bin/env python3
'''
Generators of 2D strips-and-holes geometry (initial and boundary value
arrays).

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
    halfwidth = bb[1][0] - bb[0][0]

    cl = numpy.array(cfg['centerline'])

    def rect(val, p1, p2):
        rectangle(dom, iarr,  val, p1, p2)
        rectangle(dom, barr, True, p1, p2)

    for plane in cfg['planes']:
        pitch = plane['pitch']
        thick = plane['thick']
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

            # strip center line in x
            scl = istrip * pitch

            p1 = scl - numpy.array([-shalfwid, -0.5*thick + loc])
            p2 = scl + numpy.array([ shalfwid,  0.5*thick + loc])
            rect(pot, p1, p2)

    return iarr, barr
