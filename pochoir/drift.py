try:
    from .drift_torch import solve as solve_torch
except ImportError as err:
    print('warning: pochoir.drift: no support for torch')
    print(err)

try:
    from .drift_numpy import solve as solve_numpy
except ImportError as err:
    print('warning: pochoir.drift: no support for numpy')
    print(err)


# a different implementation with scipy
from .pathfinder import solve as solve_scipy
