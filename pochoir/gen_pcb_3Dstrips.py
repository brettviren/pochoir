#!/usr/bin/env python3

import numpy
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

from .gen_pcb_quarter import draw_pcb_plane as draw_quarter

def mirror_arr_yaxis(arr):
    result = numpy.empty_like(arr)
    result[:,::-1]=arr[:,:]
    return result
    
def mirror_arr_xaxis(arr):
    result = numpy.empty_like(arr)
    result[::-1,:]=arr[:,:]
    return result

def draw_3Dstrips(arr,barr,qbarr_4,Nstrips,pcb_low_edge,pcb_width,plane):

    shape = (len(qbarr_4),len(qbarr_4[0]))
    qbarr_1 = mirror_arr_yaxis(qbarr_4)

    for s in range(2*Nstrips)[::2]:
        barr[s*shape[0]:(s+1)*shape[0],0:shape[1],pcb_low_edge] = qbarr_1[:,:,0]
        barr[s*shape[0]:(s+1)*shape[0],shape[1]:2*shape[1],pcb_low_edge] = qbarr_4[:,:,0]
        barr[(s+1)*shape[0]:(s+2)*shape[0],0:shape[1],pcb_low_edge] = qbarr_4[:,:,0]
        barr[(s+1)*shape[0]:(s+2)*shape[0],shape[1]:2*shape[1],pcb_low_edge] = qbarr_1[:,:,0]
        barr[s*shape[0]:(s+1)*shape[0],0:shape[1],pcb_low_edge+pcb_width] = qbarr_1[:,:,0]
        barr[s*shape[0]:(s+1)*shape[0],shape[1]:2*shape[1],pcb_low_edge+pcb_width] = qbarr_4[:,:,0]
        barr[(s+1)*shape[0]:(s+2)*shape[0],0:shape[1],pcb_low_edge+pcb_width] = qbarr_4[:,:,0]
        barr[(s+1)*shape[0]:(s+2)*shape[0],shape[1]:2*shape[1],pcb_low_edge+pcb_width] = qbarr_1[:,:,0]
    
    if plane==0:
        arr[(Nstrips-1)*shape[0]:Nstrips*shape[0],0:shape[1],pcb_low_edge+pcb_width] = qbarr_1[:,:,0]
        arr[(Nstrips-1)*shape[0]:Nstrips*shape[0],shape[1]:2*shape[1],pcb_low_edge+pcb_width] = qbarr_4[:,:,0]
        arr[Nstrips*shape[0]:(Nstrips+1)*shape[0],0:shape[1],pcb_low_edge+pcb_width] = qbarr_4[:,:,0]
        arr[Nstrips*shape[0]:(Nstrips+1)*shape[0],shape[1]:2*shape[1],pcb_low_edge+pcb_width] = qbarr_1[:,:,0]
    elif plane==1:
        arr[(Nstrips-1)*shape[0]:Nstrips*shape[0],0:shape[1],pcb_low_edge] = qbarr_1[:,:,0]
        arr[(Nstrips-1)*shape[0]:Nstrips*shape[0],shape[1]:2*shape[1],pcb_low_edge] = qbarr_4[:,:,0]
        arr[Nstrips*shape[0]:(Nstrips+1)*shape[0],0:shape[1],pcb_low_edge] = qbarr_4[:,:,0]
        arr[Nstrips*shape[0]:(Nstrips+1)*shape[0],shape[1]:2*shape[1],pcb_low_edge] = qbarr_1[:,:,0]

def generator(dom, cfg):
    
    plane = cfg['plane']
    r1 = int(cfg['FirstHoleRadius']/dom.spacing[0])
    r2 = int(cfg['SecondHoleRadius']/dom.spacing[0])
    pcb_width = int(cfg['PcbWidth']/dom.spacing[0])
    pcb_low_edge = int(cfg['PcbLowEdgePosition']/dom.spacing[0])
    Nstrips = cfg['Nstrips']
    
    shape_q = (int(cfg['QuarterDimX']/dom.spacing[0]),int(cfg['QuarterDimY']/dom.spacing[0]),1)
    
    arr = numpy.zeros(dom.shape)
    barr = numpy.zeros(dom.shape)
    
    #define quarter-strip
    qbarr_4 = numpy.ones(shape_q)
    draw_quarter(shape_q,qbarr_4,0,r1,r2,0,(0,1))
    
    #draw full pattern
    draw_3Dstrips(arr,barr,qbarr_4,Nstrips,pcb_low_edge,pcb_width,plane)
    
    #set top plane to be a boundary
    #barr[:,:,-1]=1

    return arr,barr
