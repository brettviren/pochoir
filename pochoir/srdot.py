#!/usr/bin/env python3

import numpy
from scipy.interpolate import RegularGridInterpolator as RGI

def dotprod(pcb_3Dstrips_domain,pcb_domain,pcb_3Dstrips_sol,pcb_drift,velo):
    #get Ew for a quarter if you look along the stripin  it slices through part with hole in the middle and takes right side up to the middle of the side hole
    
    points_ew = list()
    for num, spacing, origin in zip(pcb_3Dstrips_domain.shape, pcb_3Dstrips_domain.spacing, pcb_3Dstrips_domain.origin):
        start = origin
        stop  = origin + num * spacing
        points_ew.append(numpy.arange(start, stop, spacing))
    
    points_v = list()
    for num, spacing, origin in zip(pcb_domain.shape, pcb_domain.spacing, pcb_domain.origin):
        start = origin
        stop  = origin + num * spacing
        points_v.append(numpy.arange(start, stop, spacing))
    
    
    ew_interp = [RGI(points_ew,ew_i) for ew_i in pcb_3Dstrips_sol]
    velo_interp = [RGI(points_v,v_i) for v_i in velo]
    
    #units of charge are unclear
    q = -1
    I = []
    #This is slow, my attempt to make it interpolate for all points in path at once did not work (now it is about 13s per 10000 time ticks on mac)
    for path in pcb_drift:
        I_i = []
        for point in path:
            #V is calcualted in quarter domain as drift is defined
            V = numpy.array([velo_interp[0](point)[0],velo_interp[1](point)[0],velo_interp[2](point)[0]])
            #shift x coord of the point to accomodate for an extra strips for Ew calculation
            shift = pcb_3Dstrips_domain.shape[0]*pcb_3Dstrips_domain.spacing[0]/2.0
            point[0]=point[0]+shift
            E = numpy.array([ew_interp[0](point)[0],ew_interp[1](point)[0],ew_interp[2](point)[0]])
            i = q*numpy.dot(E,V)
            I_i.append(i)
        I.append(I_i)

    return I
