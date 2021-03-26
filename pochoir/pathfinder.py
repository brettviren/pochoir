#!/usr/bin/env python3
'''
Solve electron motion in Efiled with scipy RK method
'''

import numpy as np
from scipy.integrate import ode


def E_vect(x,efield):
    """
    Take the closest E filed o the grid to considered particle position
    """
    shape = (84,56,1000)
    dim = (2.5,1.67,30)
    i=int(x[0]*shape[0]/dim[0])-1
    j=int(x[1]*shape[1]/dim[1])-1
    k=int(x[2]*shape[2]/dim[2])-1
    print(i,j,k,efield[0][i,j,k],efield[1][i,j,k],efield[2][i,j,k])
    return efield[0][i,j,k],efield[1][i,j,k],efield[2][i,j,k]

def inBound(x,boundary):
    """
    Check if point is in or out of boundary
    """
    shape = (84,56,1000)
    dim = (2.5,1.67,30)
    i=int(x[0]*shape[0]/dim[0])-1
    j=int(x[1]*shape[1]/dim[1])-1
    k=int(x[2]*shape[2]/dim[2])-1
    indexarr = (i,j,k)
    if any(v<0 for v in indexarr):
        return 1
    if boundary[i,j,k]==0:
        return 0
    return 1


def e_of_x(x):
    return 10 * np.sign(np.sin(2 * np.pi * x / 25))

def deriv(t, Y, q, m, B, E):
    """Derivative of the state vector y according to the equation of motion:
    Y is the state vector (x, y, z, u, v, w) === (position, velocity).
    returns dY/dt.
    """
    x, y, z = Y[0], Y[1], Y[2]
    u, v, w = Y[3], Y[4], Y[5]
    
    alpha = q / m * B
    return np.array([u, v, w, E[0], alpha * w + E[1], -alpha * v+E[2]])

def calc_traj_scipy(m,q,t0,t1,dt,efield,boundary,initial_conditions):
    r = ode(deriv).set_integrator('dopri5')
    r.set_initial_value(initial_conditions, t0).set_f_params(m, q, 0.0, 10.)
    positions = []
    velocities = []
    while r.successful() and r.t < t1:
        r.set_f_params(m, q, 0.0, E_vect(r.y[:3],efield))
        r.integrate(r.t+dt)
        positions.append(r.y[:3])
        velocities.append(r.y[3:6])
        if inBound(r.y[:3],boundary)==1:
            break
    return np.array(positions),np.array(velocities)


def solve(ipos,ivel,barr,efield,time,step):


    t0=0.0
    
    positions = []
    velocities = []
    print(ipos,ivel)
    for ip in ipos:
        print(ip)
    for ip,iv in zip(ipos,ivel):
        p,v=calc_traj_scipy(1.0, 1.0,t0,time,step,efield,barr,np.concatenate((ip, iv)))
        positions.append(p)
        velocities.append(v)
    #Debug Plots
   # import matplotlib as mpl
   # import matplotlib.pyplot as plt
   # from mpl_toolkits.mplot3d import Axes3D
   # fig = plt.figure()
   # ax = fig.add_subplot(111, projection='3d')
   # for position in positions:
   #     ax.plot3D(position[:, 0], position[:, 1], position[:, 2])
   # plt.xlabel('x')
   # plt.ylabel('y')
   # ax.set_zlabel('z')
   # plt.show()
    return positions,velocities

