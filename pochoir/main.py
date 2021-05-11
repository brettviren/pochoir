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

from pathlib import Path

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
        self.instore_path = Path(instore).resolve()
        if outstore is None:
            self.instore = persist.store(instore, 'a')
            self.outstore = self.instore
        else:
            self.instore = persist.store(instore, 'r')
            self.outstore = persist.store(outstore, 'w')
        self.device = device

    @property
    def instore_name(self):
        return str(self.instore_path)

    def key(self, fname):
        p = Path(fname).resolve()
        try:
            got = p.relative_to(self.instore_path)
        except ValueError:
            return fname        # assume already a key
        return str(got.with_suffix(""))

    def get(self, key):
        '''
        Return in input array at key.
        '''
        key = self.key(key)
        return self.instore.get(key)

    def get_domain(self, key):
        '''
        Return a domain from arrays at key.

        Key should be for a group of datasets or directory of files
        describing a domain.
        '''
        key = self.key(key)
        _, md = self.instore.get(key, True)
        # dom = Domain(self.get(key + "/shape"),
        #              self.get(key + "/spacing"),
        #              self.get(key + "/origin"))
        shape = md.pop("shape")
        spacing = md.pop("spacing")
        origin = md.pop("origin", None)
        dom = Domain(shape, spacing, origin)
        return dom

    def put_domain(self, key, dom):
        '''
        Put a domain to key in store.

        Note, this saves to a group of datasets (directory of files)
        '''
        self.put(key, (), **dom.asdict)
        # self.put(key + "/shape", dom.shape)
        # self.put(key + "/spacing", dom.spacing)
        # self.put(key + "/origin", dom.origin)

    def put(self, key, array, **metadata):
        '''
        Save an array to key in output store.
        '''
        key = self.key(key)
        return self.outstore.put(key, array, **metadata)

