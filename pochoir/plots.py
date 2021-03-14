import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

def image(arr, fname):
    plt.clf()
    #plt.title("initial")
    plt.imshow(arr, interpolation='none', aspect='auto')
    plt.colorbar()
    plt.savefig(fname)
