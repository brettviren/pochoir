#!/usr/bin/env python
'''
Low-level functions for arrays.  
'''

from . import units

# Ideally, this is only module to import these two:
import numpy
import torch

# import limited numpy api.
# fixme: need to rethink this....
ones = numpy.ones
zeros = numpy.zeros
linspace = numpy.linspace
meshgrid = numpy.meshgrid

def module(array):
    '''
    Return either numpy or torch module matching type of array
    '''
    if isinstance(array, torch.Tensor):
        return torch
    if isinstance(array, numpy.ndarray):
        return numpy


def fromstr1(string, dtype=float):
    '''
    Parse string as 1d list of numbers, return array

    Numbers may have unit names multiplied
    '''
    s = [dtype(eval(s.strip(), units.__dict__)) for s in string.split(",") if s.strip()]
    return to_numpy(s)


def to_numpy(array):
    '''
    Return array or a new numpy array if not already one.
    '''
    if isinstance(array, torch.Tensor):
        return array.to('cpu').numpy()
    return numpy.array(array)


def to_torch(array):
    '''
    Return array or a new torch tensor if not already one.
    '''
    return torch.tensor(array)
    

def gradient(array, spacing = None):
    '''
    Return the finite difference gradient of the array.
    '''
    if isinstance(array, numpy.ndarray):
        return numpy.array(numpy.gradient(array))

    # Amazingly, PyTorch has no equivalent.  An alternative solution
    # is to reimplment numpy.gradient() in terms of tensor slicing and
    # arithmetic operations.  At the cost of possible GPU->CPU->GPU
    # transit, for now we do the dirty:
    a = array.to('cpu').numpy()
    gvec = numpy.gradient(a)
    if spacing is not None:
        print(spacing)
        gvec = [numpy.array(v/s) for v,s in zip(gvec, spacing)]
    g = numpy.array(gvec)
    return torch.tensor(g, device=array.device)
    
def vmag(vfield):
    '''
    Return magnitude of vector field as scalar field.

    The vfield is an N-list of N-d arrays, each giving one dimension's component.
    '''
    c2s = [c*c for c in vfield]
    tot = numpy.zeros_like(c2s[0])
    for c2 in c2s:
        tot += c2
    return numpy.sqrt(tot)


def dup(array):
    '''
    Return a copy of the array
    '''
    if isinstance(array, torch.Tensor):
        return torch.clone(array)
    return numpy.copy(array)


def core_slices1(array):
    '''
    Return slices with core shape of and array made one cell in each
    direction.
    '''
    return tuple([slice(1,s-1) for s in array.shape])


def core1(array):
    '''
    Return core part of array, removing a 1 element pad
    '''
    return array[core_slices1(array)]


def pad1(array):
    '''
    Return a new array with every dimension increased by 1 on either
    edge and central value holding array.
    '''
    mod = module(array)
    shape = [s+2 for s in array.shape]
    padded = mod.zeros(shape)
    padded[core_slices1(padded)] = array
    return padded
