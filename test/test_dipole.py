#!/usr/bin/env pytest
import numpy
import pochoir

from pochoir.fdm_numpy import solve


def test_dipole():
    dom = pochoir.domain.Domain((100,100), 0.1)
    print("DOMAIN:",dom)

    iva, bva = pochoir.examples.ex_dipole(dom)
    print("IVA/BVA:",iva, bva)

    edge_cond = (True, True)
    precision = 0.001
    epoch = 100
    nepochs = 100
    pot, pot_err = solve(iva, bva, edge_cond,
                         precision, epoch, nepochs)
    

    efield = pochoir.arrays.gradient(pot, dom.spacing)
    emag = pochoir.arrays.vmag(efield)
    temperature = 89*pochoir.units.K
    mu = pochoir.lar.mobility(emag, temperature)
    velo = [e*mu for e in efield]


    times = numpy.arange(0.0,10.0,0.1)
    paths = list()
    for p in numpy.arange(0.,10.,1.):
        start = (p,p)
        print("start:",start)
        path = pochoir.drift_torch.solve(dom, start, velo, times)
        paths.append(path.numpy())
    numpy.savez("test_dipole.npz", paths)
