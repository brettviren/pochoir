#!/usr/bin/env python3
'''
A high level interface to pochoir.

This supports command line usage policy encoded in __main__ but could
be used in larger applications.

Basically this holds CLI commands but without any specify CLI
framework dependency (ie, no click).
'''


from . import persist 
from . import arrays
from . domain import Domain

class Main:
    '''
    Main entry point (almost) to pochoir.  

    See also __main__
    '''

    def __init__(self, instore, outstore=None, device='cpu'):
        '''
        Create a pochoir main.

            - instore gives file name providing input storage for
              input and possibly output of an operation.

            - outstore gives file name providing output storage.  If
              given the input store is made readonly.
        '''
        if outstore is None:
            self.instore = persist.store(instore, 'a')
            self.outstore = self.instore
        else:
            self.instore = persist.store(instore, 'r')
            self.outstore = persist.store(outstore, 'w')
        self.device = device

    def get(self, key):
        '''
        Return in input array at key.
        '''
        return arrays.to_torch(self.instore.get(key)).to(self.device)

    def get_domain(self, key):
        '''
        Return a domain from arrays at key.

        Key should be for a group of datasets or directory of files
        describing a domain.
        '''
        return Domain(self.get(key + "/shape"),
                      self.get(key + "/origin"),
                      self.get(key + "/spacing"),
                      self.get(key + "/first"))

    def put_domain(self, key, dom):
        '''
        Put a domain to key in store.

        Note, this saves to a group of datasets (directory of files)
        '''
        self.put(key + "/shape", dom.shape)
        self.put(key + "/origin", dom.origin)
        self.put(key + "/spacing", dom.spacing)
        self.put(key + "/first", dom.first)

        


    def put(self, key, array, **metadata):
        '''
        Save an array to key in output store.
        '''
        return self.outstore.put(key, array, **metadata)

