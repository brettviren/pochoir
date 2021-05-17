from pochoir import arrays

def edge_condition(arr, *periodic):
    '''
    Apply N edge conditions (periodic if True, else fixed) to N-D array.
    '''
    np = len(periodic)
    na = len(arr.shape)
    if np != na:
        raise ValueError(f"dimension mismatch: {np} != {na}")
    
    # whole array slice
    slices = [slice(0,s) for s in arr.shape]
    for dim, per in enumerate(periodic):
        n = arr.shape[dim]
        src1 = list(slices)
        src2 = list(slices)
        dst1 = list(slices)
        dst2 = list(slices)

        dst1[dim] = slice(0,1)
        src1[dim] = slice(n-2, n-1)

        dst2[dim] = slice(n-1,n)
        src2[dim] = slice(1,2)

        if per:
            arr[tuple(dst1)] = arr[tuple(src1)]
            arr[tuple(dst2)] = arr[tuple(src2)]
        else:                   # fixed
            arr[tuple(dst1)] = arr[tuple(src2)]
            arr[tuple(dst2)] = arr[tuple(src1)]


def stencil(array, res = None):
    '''
    Return sum of 2N views of N-D array.

    Each view for a dimension is offset by +/- one cell.

    The shape of the returned array is reduced by two indices in each
    dimension.  If res is given, it must be of reduced size and it
    will be used to hold the result.
    '''
    # whole array slice
    slices = [slice(1,s-1) for s in array.shape]
    nd = len(slices)
    norm = 1/(2*nd)

    if res is None:
        core_shape = [s-2 for s in array.shape]
        amod = arrays.module(array)
        res = amod.zeros(core_shape)
    else:
        res[:] = 0

    for dim, n in enumerate(array.shape):
        pos = list(slices)
        pos[dim] = slice(2,n)
        res += array[tuple(pos)]

        neg = list(slices)
        neg[dim] = slice(0,n-2)
        res += array[tuple(neg)]

    res *= norm
    return res
