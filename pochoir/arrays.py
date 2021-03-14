#!/usr/bin/env python
'''
pochoir arrays
'''

import numpy
import torch

def module(array):
    '''
    Return either numpy or torch module matching type of array
    '''
    if isinstance(array, torch.Tensor):
        return torch
    if isinstance(array, numpy.ndarray):
        return numpy


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
    
def gradient(array):
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
    g = numpy.array(numpy.gradient(a))
    return torch.tensor(g, device=array.device)
    

def domain(lss):
    '''
    Return a domain array corresponding to the linear spaces
    '''
    # fixme: do something sensible for torch....
    lss = [numpy.linspace(*ls, endpoint=False) for ls in lss]
    return numpy.meshgrid(*lss)

def dup(array):
    '''
    Return a copy of the array
    '''
    if isinstance(array, torch.Tensor):
        return torch.clone(array)
    return numpy.copy(array)

def core_slices1(array):
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
