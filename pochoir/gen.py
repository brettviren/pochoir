#!/usr/bin/env python
'''
Collect various generators.

These simply combine generator functions into a common namespace.

See gen() in __main__
'''


from .gen_sandh import generator as sandh
from .gen_sandh2d import generator as sandh2d

from .gen_pcb_quarter import generator as pcb_quarter
from .gen_pcb_2Dstrips import generator as pcb_2D
from .gen_pcb_3Dstrips import generator as pcb_3D

