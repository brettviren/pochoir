import numpy

def ex_caps():
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

