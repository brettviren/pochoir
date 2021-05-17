
from pochoir.fdm_numpy import solve as solve_numpy

try:
    from pochoir.fdm_torch import solve as solve_torch
except ImportError as err:
    print('warning: pochoir.fdm: no support for torch')
    print(err)

try:
    from pochoir.fdm_numba import solve as solve_numba
except ImportError as err:
    print('warning: pochoir.fdm: no support for numba')
    print(err)

try:
    from pochoir.fdm_cupy import solve as solve_cupy
except ImportError as err:
    print('warning: pochoir.fdm: no support for cupy')
    print(err)

try:
    from pochoir.fdm_cumba import solve as solve_cumba
except ImportError as err:
    print('warning: pochoir.fdm: no support for cumba (numba+cupy)')
    print(err)

