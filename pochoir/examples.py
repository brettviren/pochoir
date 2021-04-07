#!/usr/bin/env python3
'''
This provides a grab bag of functions that build example
initial/boundary value arrays.
'''

import numpy

def ex_dipole(dom, field="dr"):
    '''
    Produce a dipole problem with a given field in ("dr","w1","w2").
    '''
    pot1=+100
    pot2=-100
    if field == "w1":
        pot1=1
        pot2=0
    if field == "w2":
        pot1=0
        pot2=1

    bb = dom.bb
    print(bb, dom.shape)
    d = bb[1] - bb[0]
    p1 = 0.1*d + bb[0]
    p2 = 0.9*d + bb[0]

    ind1 = tuple(dom.index(p1))
    ind2 = tuple(dom.index(p2))
    print(p1,ind1)
    print(p2,ind2)

    iva = numpy.zeros(dom.shape, dtype=float)
    bva = numpy.zeros(dom.shape, dtype=bool)

    iva[ind1] = pot1
    iva[ind2] = pot2
    bva[ind1] = True
    bva[ind2] = True    

    return iva, bva

def ex_dipoledr(dom):
    return ex_dipole(dom, "dr")
def ex_dipolew1(dom):
    return ex_dipole(dom, "w1")
def ex_dipolew2(dom):
    return ex_dipole(dom, "w2")

def ex_sandh(dom=None):
    '''
    A strip+hole 3D example
    '''
    # units are mm
    sep = 0.05
    strip_width = 5
    strip_length = 2
    rad = 1

    cat_pos = 100
    strip_pos = 30              # strip center
    strip_thick = 0.3
    elec_thick = 0.1
    ind_pos = strip_pos + 0.5*(strip_thick+elec_thick)
    col_pos = strip_pos - 0.5*(strip_thick+elec_thick)
    gnd_pos = 0

    
    # 500 v/cm
    cat_pot = 50 * (cat_pos - gnd_pos)
    # this is bogus:
    ind_pot = 50 * (ind_pos - gnd_pos) + 100
    col_pot = 50 * (col_pos - gnd_pos) - 100

    # [101, 41, 2001]
    shape = [1+int(strip_width/sep),
             1+int(strip_length/sep),
             1+int((cat_pos-gnd_pos)/sep)]
    arr = numpy.ones(shape)     # use 1.0 as non-boundary value

    def xi(x):
        return int((x+0.5*strip_width)/sep)
    def yi(y):
        return int((y+0.5*strip_length)/sep)
    def zi(z):
        return int(z/sep)

    arr[:,:,zi(cat_pos)] = cat_pot
    arr[:,:,zi(ind_pos)] = ind_pot
    arr[:,:,zi(col_pos)] = col_pot
    arr[:,:,zi(gnd_pos)] = 0.0
    
    # square holes for now
    arr[xi(-0.5*strip_width) :xi(-0.5*strip_width+rad),
        yi(-0.5*strip_length):yi(-0.5*strip_length+rad),
        zi(ind_pos):zi(col_pos)] = 1.0
    arr[xi(+0.5*strip_width) :xi(+0.5*strip_width+rad),
        yi(+0.5*strip_length):yi(+0.5*strip_length+rad),
        zi(ind_pos):zi(col_pos)] = 1.0

    barr = numpy.ones(shape)
    barr[arr == 1.0] = 0

    return arr,barr


def ex_caps(dom=None):
    '''
    Kind of a spiral of capacitors
    '''
    pots = (-1000, 1000)
    shape= (100, 100)
    arr = numpy.zeros(shape)
    spot = 0
    sign = 1
    for step in range(5):

        sign *= -1

        arr[spot           ,spot:shape[1]-spot-1] = sign*pots[0]
        arr[shape[0]-spot-1,spot:shape[1]-spot-1] = sign*pots[1]

        spot += 5

        arr[spot:shape[0]-spot-1,            spot] = sign*pots[0]
        arr[spot:shape[1]-spot-1, shape[1]-spot-1] = sign*pots[1]

        spot += 5

    barr = numpy.ones(shape)
    barr[arr == 0] = 0

    return arr,barr

