try:
    from .drift_torch import solve as torch
except ImportError as err:
    print('warning: pochoir.drift: no support for torch')
    print(err)

from .pathfinder import solve as numpy
