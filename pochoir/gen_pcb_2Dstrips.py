#!/usr/bin/env python3

import numpy

def draw_plane(arr,z,potential):
    arr[:,z]=potential

def draw_hole_pattern(arr,dom,z,widthX,widthZ,holeWidth,Nstrips,potential_midle,potential_sides,conf):
    
    plateWidth = widthX-holeWidth
    shape = dom.shape
    spacing = dom.spacing[0]
    
    holePattern = []
    #define hole pattern in mm units
    if conf==0:
        hole = numpy.array([0.0,holeWidth/2])
        holePattern.append(hole)
        for i in range(Nstrips-1):
            hole_a=numpy.array([holeWidth/2+plateWidth+i*(holeWidth+plateWidth),3*holeWidth/2+plateWidth+i*(holeWidth+plateWidth)])
            holePattern.append(hole_a)
        hole_f=numpy.array([holePattern[-1][1]+plateWidth,holePattern[-1][1]+plateWidth+holeWidth/2])
        holePattern.append(hole_f)
    if conf==1:
        for i in range(Nstrips):
            hole=numpy.array([(plateWidth/2+i*(holeWidth+plateWidth)),(plateWidth/2+holeWidth+i*(holeWidth+plateWidth))])
            holePattern.append(hole)
    #apply grid to the defined hole pattern
    for i in range(int(shape[0])):
        l=i*spacing
        isHole = False
        for h in holePattern:
            if (l>=h[0] and l<=h[1]):
                isHole=True
                break
        if(isHole):
            arr[i][z] = 0
        else:
            arr[i][z] = potential_sides
     
    #fill the middle strip
    if conf==0:
        init = int(10.0*widthX/spacing+holeWidth/2.0/spacing)
        final = int(10.0*widthX/spacing+holeWidth/(2.0*spacing)+plateWidth/spacing+1)
        arr[init:final,z] = potential_midle
    if conf==1:
        init_1 = int(10.0*widthX/spacing)
        final_1 = int(10.0*widthX/spacing+plateWidth/(2.0*spacing)+1)
        init_2 = final_1+int(holeWidth/spacing)
        final_2 = int(init_2+plateWidth/(2.0*spacing)+1)
        arr[init_1:final_1,z] = potential_midle
        arr[init_2:final_2,z] = potential_midle
    

def generator(dom, cfg):
    """
    need to pass strip width in X and Z, holewidth in mm and configuration of 2D plane
    conf=0 with quaterholes on a sides and dimHole providing the dim of the left hole, conf=1 with hole in the middle
    plane = 0 is induction , plane = 1 is collection
    """
    arr = numpy.zeros(dom.shape)
    barr = numpy.zeros(dom.shape)
    
    plane = cfg['plane'];  # check which plane to set to 1V (coll/ind)
    conf= cfg['config']    # 2d view configuration
    widthX = cfg['StripWidthX'] #strip width in X
    widthZ = cfg['StripWidthZ'] # strip width in Z
    positionZ = cfg['LowEdgePosition'] # lowes position of the strip in Z in mm
    holeWidth = cfg['HoleDiameter']    # hole diameter in the strip
    Nstrips = cfg['Nstrips']           # total number of strips
        
    shape = dom.shape
    spacing = dom.spacing[0]
    z_i=int(positionZ/spacing)
    z_f=int((positionZ+widthZ)/spacing)
    
    
    if plane==0:
        draw_hole_pattern(arr,dom,z_i,widthX,widthZ,holeWidth,Nstrips,0,0,conf)
        draw_hole_pattern(barr,dom,z_i,widthX,widthZ,holeWidth,Nstrips,1,1,conf)
    
        draw_hole_pattern(arr,dom,z_f,widthX,widthZ,holeWidth,Nstrips,1,0,conf)
        draw_hole_pattern(barr,dom,z_f,widthX,widthZ,holeWidth,Nstrips,1,1,conf)
    elif plane==1:
        draw_hole_pattern(arr,dom,z_i,widthX,widthZ,holeWidth,Nstrips,1,0,conf)
        draw_hole_pattern(barr,dom,z_i,widthX,widthZ,holeWidth,Nstrips,1,1,conf)
    
        draw_hole_pattern(arr,dom,z_f,widthX,widthZ,holeWidth,Nstrips,0,0,conf)
        draw_hole_pattern(barr,dom,z_f,widthX,widthZ,holeWidth,Nstrips,1,1,conf)

        
    draw_plane(barr,shape[1]-1,1)

    return arr,barr
