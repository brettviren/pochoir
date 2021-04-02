#!/usr/bin/env pytest
import numpy
import pochoir


def test_dipole():
    dom = pochoir.domain.Domain((1000,1000), 0.1)
    print("DOMAIN:",dom)

    iva, bva = pochoir.examples.ex_dipole(dom)
    print("IVA/BVA:",iva, bva)

    edge_cond = (True, True)
    precision = 0.1
    epoch = 100
    nepochs = 10
    pot, pot_err = pochoir.fdm.solve(iva, bva, edge_cond,
                                     precision, epoch, nepochs)
    

    efield = pochoir.arrays.gradient(pot, dom.spacing)
    emag = pochoir.arrays.vmag(efield)
    temperature = 89*pochoir.units.K
    mu = pochoir.lar.mobility(emag, temperature)
    velo = [e*mu for e in efield]


    start = (12.,12.)
    times = numpy.arange(0,10,.1)
    path = pochoir.drift_torch.solve(dom, start, velo, times)
    print (path)
