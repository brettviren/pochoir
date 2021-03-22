#!/usr/bin/env python3
'''
A 2-view strips and holes generator with methods for 2D and 3D.

Strips in each plane are constrained to be orthogonal and the central
grid point sees a crossign point of two strip centerlines.

This generator takes a configuration with these top attributes:

    - planes :: array of plane objects described below

The plane list of objects each describing a plane with attributes:

    - axis :: the array axis perpendicular to the plane

    - height :: position along that axis for the plane center

    - thick :: thickness of plane

    - potential :: the potential value for the plane

    - strips :: a strips object, if any (see below)

    - holes :: a holes object, if any (see below)

A "strips" object:

    - paxis :: the array axis perpendicular to the strips direction
      and plane (ie, in pitch direction)

    - pitch :: the transverse distance between strip centerlines

    - gap :: distance between neighboring strips

    - offset :: position from central grid point to strip0 centerline

    - weighting :: if true, only set plane potential on central strip,
      all others get zero.

A "holes" object:

    - radius :: radius of the holes

    - offset :: a 2-tuple holding distance offset from central grid
      point in [x,y] to a hole

    - spacing :: a 2-tuple holding distance between holes
'''

from pochoir.shape_schema import rectangle

def twod_holes(dom, name,  axis, height, thick, holes, potential=None, **kwds):
    '''
    Return shape list and value dict for 2D holes
    '''
    paxis = (axis+1)%2
    radius = holes['radius']
    offset = holes['offset'][paxis]
    spacing = holes['spacing'][paxis]

    shapes = list()

    center = dom.point(dom.shape//2)
    s0p = center[paxis] + offset
    
    bb = dom.bb
    for count, sp in enumerate(numpy.arange(range(s0p, bb[1][paxis], spacing))):
        if not count:
            sname = f'{name}-hole-0'
        else:
            sname = f'{name}-hole-p{count}'
        p1=list(p1)
        p2=list(p2)
        p1[paxis] = sp - radius
        p2[paxis] = sp + radius
        shapes.append(rectangle(sname, p1, p2))
            
    for count, sp in enumerate(numpy.arange(range(s0p - spacing, bb[0][paxis], -spacing))):
        sname = f'{name}-hole-m{count+1}'
        p1=list(p1)
        p2=list(p2)
        p1[paxis] = sp - radius
        p2[paxis] = sp + radius
        shapes.append(rectangle(sname, p1, p2))
    
    # holes, so all values are non-existent by definition
    return shapes, dict()

def twod_strips(dom, name, axis, height, thick, strips, potential=None, **kwds):
    '''
    Return shape list and value dict for 2D plane of strips
    '''
    paxis = strips['paxis']
    if axis == paxis:
        raise ValueError("Plane normal axis and pitch axis can not coincide")
    offset = strips['offset']
    pitch = strips['pitch']
    gap = strips['gap']
    weighting = strips.get('weighting', False)

    shapes = list()
    values = dict()

    center = dom.point(dom.shape//2)
    s0p = center[paxis] + offset
    wid = pitch-gap

    # strip 0
    p1 = [None]*2
    p2 = [None]*2
    p1[axis] = height-0.5*thick
    p2[axis] = height+0.5*thick
    p1[paxis] = s0p - 0.5*wid
    p2[paxis] = s0p + 0.5*wid

    sname = name + "-strip0"
    shapes.append(rectangle(sname, p1, p2))
    if potential is not None:
        values[name] = potential

    bb = dom.bb
    for count, sp in enumerate(numpy.arange(range(s0p + pitch, bb[1][paxis], pitch))):
        sname = f'{name}-strip-p{count+1}'
        p1=list(p1)
        p2=list(p2)
        p1[paxis] = sp - 0.5*wid
        p2[paxis] = sp + 0.5*wid
        shapes.append(rectangle(sname, p1, p2))
        if not weighting and potential is not None:
            values[name] = potential
            
    for count, sp in enumerate(numpy.arange(range(s0p + pitch, bb[0][paxis], -pitch))):
        sname = f'{name}-strip-m{count+1}'
        p1=list(p1)
        p2=list(p2)
        p1[paxis] = sp - 0.5*wid
        p2[paxis] = sp + 0.5*wid
        shapes.append(rectangle(sname, p1, p2))
        if not weighting and potential is not None:
            values[name] = potential
        
    return shapes, values



def twod_plane(dom, name, axis, height, thick, potential=None, **kwds):
    '''
    Return shape list and value dict for a 2D solid plane
    '''

    p1 = [None]*2
    p2 = [None]*2

    p1[axis] = height-0.5*thick
    p2[axis] = height+0.5*thick

    bb = dom.bb
    axis1 = (axis+1)%2
    p1[axis1] = bb[0][axis1]
    p2[axis1] = bb[1][axis1]

    s = [rectangle(name, p1, p2)]
    v = dict()
    if potential is not None:
        v[name] = potential
    return s,v


def gen_twod(dom, cfg):
    '''
    Generate a 2D strips and holes for 2-view
    '''
    # note: this center may not be on a grid point
    center = dom.point(dom.shape/2)

    shapes = list()
    values = dict()
    
    for iplane, plane in enumerate(cfg["planes"]):
        strips = plane.get('strips', None)
        if strips:
            s,v = twod_strips(dom, f'plane{iplane}', **plane)
        else:
            s,v = twod_plane(dom, f'plane{iplane}', **plane)
        shapes.append(s)
        values.update(v)

        holes = plane.get('holes', None)
        if holes:
            s,v = twod_holes(dom, f'plane{iplane}', **plane)
        shapes.append(s)
        values.update(v)

def generator(dom, cfg):
    if len(dom.shape) == 2:
        return gen_twod(dom, cfg)
    raise ValueError("sandh only supports 2D for now")
