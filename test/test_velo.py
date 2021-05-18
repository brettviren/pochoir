#!/usr/bin/env pytest

import numpy
import pochoir
from pochoir import units
from pochoir.fdm_numpy import solve

def test_velo():

    emag = 500*units.V/units.cm
    wid = 5*units.cm
    sep = 10*units.cm
    grid = 1*units.mm
    dsiz = (sep, wid)
    shape = (int(sep/grid), int(wid/grid))
    mid = int(0.5*wid/grid)
    dom = pochoir.domain.Domain(shape, grid)


    iva = numpy.zeros(shape)
    iva[0] = -0.5*emag*sep
    iva[-1] = 0.5*emag*sep
    bva = numpy.zeros(shape, dtype=bool)
    bva[0] = bva[-1] = True

    edge_cond = (False, True)
    precision = 0.001
    epoch = 100
    nepochs = 100
    pot, pot_err = solve(iva, bva, edge_cond,
                         precision, epoch, nepochs)
    
    efield = pochoir.arrays.gradient(pot, dom.spacing)
    emag = pochoir.arrays.vmag(efield)
    temperature = 89*units.K
    mu = pochoir.lar.mobility(emag, temperature)
    velo = [e*mu for e in efield]

    numpy.savez("test_velo.npz", iva=iva,bva=bva,
                pot=pot,pot_err=pot_err,efield=efield,
                emag=emag,velo=velo)

    # first column
    vy = velo[0][:,mid]
    vx = velo[1][:,mid]

    close_y = numpy.abs(vy-1.6*units.mm/units.us)

    assert numpy.max(vy/(units.mm/units.us)) < 1.6
    assert numpy.min(vy/(units.mm/units.us)) > 1.5
    assert numpy.max(vx) < 0.0001

