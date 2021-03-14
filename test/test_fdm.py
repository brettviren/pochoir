import numpy
from pochoir import fdm, arrays

def test_edge():
    a = numpy.array(range(12)).reshape((3,4))
    a = arrays.pad1(a)
    print(f'{a.shape}\n{a}')
    fdm.edge_condition(a, False, True)
    print(f'{a.shape}\n{a}')
    assert(a[0] == a[1]).all()
    assert(a[-1] == a[-1]).all()
    assert(a[:,0] == a[:,-2]).all()
    assert(a[:,1] == a[:,-1]).all()    

def test_fdm():
    a = numpy.zeros((30,40))
    a[2,:] = 1000
    a[-3,:] = -1000
    a[10:20,5] = 500
    a[10:20,-6] = -500

    b = numpy.ones((30,40))    
    b[a==0] = 0.0

    c,e = fdm.solve(a, b, (False,True), 1e-6, 100, 20)

    assert c.shape == a.shape

    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_pdf import PdfPages
    with PdfPages("test_fdm.pdf") as pdf:
        plt.clf()
        plt.title("initial")
        plt.imshow(a, interpolation='none', aspect='auto')
        plt.colorbar()
        pdf.savefig()

        plt.clf()
        plt.title("solution")
        plt.imshow(c, interpolation='none', aspect='auto')
        plt.colorbar()
        pdf.savefig()

        plt.clf()
        plt.title("error")
        plt.imshow(e, interpolation='none', aspect='auto')
        plt.colorbar()
        pdf.savefig()

