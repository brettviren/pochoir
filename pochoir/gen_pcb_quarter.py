#!/usr/bin/env python3

import numpy
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

def draw_quarter_circle(x0,y0,r):
    """
    Sorted by x-index IDs of an apper-right quarter-circle on a given grid
    x0,y0,r are in index units
    
    draws IV quadrant
    """
    x=0
    y=r
    d=3-2*r
    id_circ1=[]
    shifted=[]
    id_circ1.append((x,y))
    while x<=y :
        if d<0:
            d=d+4*x+6
            x=x+1
            id_circ1.append((x,y))
            id_circ1.append((y,x))
        if d>=0:
            d=d+4*(x-y)+6
            x=x+1
            y=y-1
            id_circ1.append((x,y))
            id_circ1.append((y,x))
    id_circ1.sort(key = lambda x: x[0])
    for id in id_circ1:
        sh=(id[0]+x0,id[1]+y0)
        shifted.append(sh)
    return shifted

def mirror_xaxis(id_circ1,x0,y0,r):
    """
    mirror quarter-circle of Xaxis
    """
    id_circ2=[]
    for id in id_circ1:
        id_circ2.append((id[0],y0-(id[1]-y0)))
    return id_circ2

def mirror_yaxis(id_circ1,x0,y0,r):
    """
    mirror quarter-circle of Yaxis
    """
    id_circ2=[]
    for id in id_circ1:
        id_circ2.append((x0-(id[0]-x0),id[1]))
    return id_circ2


def mirror_center(id_circ1,x0,y0):
    """
    mirror quarter-circle of the center point
    """
    id_circ2=[]
    for id in id_circ1:
        id_circ2.append((x0-(id[0]-x0),y0-(id[1]-y0)))
    return id_circ2

def fill_area(arr,barr,val):
    """
    fill 2D area inside the boundary
    
    barr should be constructed such, [x,[y_start,y_stop]] sorted in increasing x
    """
    for b in barr:
        arr[b[0],b[1][0]:b[1][1]]=val

def draw_plane(arr,z,val):
    """
    Fill 1 plane
    """
    arr[:,:,z]=val

def form_quarter_boundary(indx,x0,y0):
    dx = indx[0][0]-x0 # x index from center
    dy = indx[0][1]-y0   # y index from center
    barr = []
    if dx>=0 and dy>0:
        for idx in indx:
            yarr = (y0,idx[1])
            xarr = (idx[0],yarr)
            barr.append(xarr)
    if dx>=0 and dy<0:
        for idx in indx:
            yarr = (idx[1],y0)
            xarr = (idx[0],yarr)
            barr.append(xarr)
    if dx<0 and dy>=0:
        for idx in indx:
            yarr = (y0,idx[1])
            xarr = (idx[0],yarr)
            barr.append(xarr)
    if dx<0 and dy<=0:
        for idx in indx:
            yarr = (idx[1],y0)
            xarr = (idx[0],yarr)
            barr.append(xarr)
    return barr


def draw_pcb_plane(shape,arr,z,r1,r2,free,val):
    if free==1:
        draw_plane(arr,z,val[0])
    else:
        draw_plane(arr,z,val[1])
        id_circ1=draw_quarter_circle(0,0,r1)
        id_circ2=draw_quarter_circle(shape[0]-1,shape[1]-1,r2)
        id_circ2_m=mirror_center(id_circ2,shape[0]-1,shape[1]-1)
        barr1=form_quarter_boundary(id_circ1,0,0)
        barr2=form_quarter_boundary(id_circ2_m,shape[0]-1,shape[1])
        fill_area(arr,barr1,0)
        fill_area(arr,barr2,0)

def draw_3D_pcb(arr,shape,r1,r2,v_cath,v_pcb,v_an,pcb_width):
    volt = (v_cath,v_pcb)
    for z in range(shape[2]-1):
        if z<pcb_width:
            draw_pcb_plane(shape,arr,z,r1,r2,0,volt)
        else:
            draw_pcb_plane(shape,arr,z,r1,r2,1,volt)
    draw_pcb_plane(shape,arr,shape[2]-1,r1,r2,1,(v_an,0))

def generator(dom, cfg):
    shape=(len(dom[0]),len(dom[0][0]),len(dom[0][0][0]))
    arr = numpy.zeros(shape)
    barr = numpy.ones(shape)
    draw_3D_pcb(arr,shape,41,41,2000,-1,-15000,10)
    barr[arr == 0] = 0

    return arr,barr
