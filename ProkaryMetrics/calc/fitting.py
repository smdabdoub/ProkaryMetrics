'''
Created on Jul 24, 2011

@author: shareef
'''
from render.basic import createEllipsoid, createSphere
from store import DataStore
from vector import Vec3f

import csv
import math
from numpy import *
import numpy.linalg as la
import vtk

def fitEllipsoid(actorRadius):
    """
    Fit an ellipsoid to the existing recorded bacteria for estimation 
    of volume and shape.
    
    :@rtype: tuple -> (vtkActor, vtkActor)
    :@return: parametric ellipsoid actor and text actor displaying the volume
    """
    points = [[],[],[]]
    
    for bact in DataStore.Bacteria():
        points[0].extend([marker.x for marker in bact.Markers])
        points[1].extend([marker.y for marker in bact.Markers])
        points[2].extend([marker.z for marker in bact.Markers])  
    
    # output data to file
    with open('ellipse.csv', 'w') as e:
        writer = csv.writer(e, delimiter=',')
        writer.writerows(points)
    
    
    
    
    A, center = minimumVolumeEllipsoid(array(points), tol=0.001)
    r, RM = extractEllipsoidParams(A)
    radius = Vec3f(r)
    center = Vec3f(list(center[:,0]))
    
    volume = 4.0/3.0 * math.pi * radius.x * radius.y * radius.z
    bactVol = bacterialVolume(actorRadius)
    
    ibcDensity = bactVol/volume
    
    #TODO: apply rotation matrix RM
    rm = vtk.vtkMatrix4x4()
    rm.DeepCopy((RM[0,0], RM[0,1], RM[0,2], center.x,
                 RM[1,0], RM[1,1], RM[1,2], center.y,
                 RM[2,0], RM[2,1], RM[2,2], center.z,
                    0   ,    0   ,    0   , 1))
    
    ellipsoidTextMapper = vtk.vtkTextMapper()
    ellipsoidTextMapper.SetInput("Type: %s\nVolume: %d\nRadius: %s\nv/v: %f" % 
                                 (ellipsoidType(radius), volume, str(radius), ibcDensity))
    ellipsoidTextMapper.GetTextProperty().SetJustificationToCentered()
    ellipsoidTextMapper.GetTextProperty().SetVerticalJustificationToCentered()
    ellipsoidTextMapper.GetTextProperty().SetColor(0.75, 0.75, 0.75)
    ellipsoidTextMapper.GetTextProperty().SetFontSize(14)
    ellipsoidTextActor = vtk.vtkActor2D() 
    ellipsoidTextActor.SetMapper(ellipsoidTextMapper)    
    ellipsoidTextActor.GetPositionCoordinate().SetCoordinateSystemToWorld()
    ellipsoidTextActor.GetPositionCoordinate().SetValue(center.x-30, center.y-30, center.z)
    
    print "Ellipsoid type: ", ellipsoidType(radius)
    print "Ellipsoid radii: ", str(radius)
    print "Ellipsoid center: ", str(center)
    print "Ellipsoid Volume: ", volume
    print "Bacteria Volume: ", bactVol
    print "Bacterial Mass to Ellipsoid Volume ratio: ", ibcDensity
    
    ellipsoid = createEllipsoid(radius, Vec3f())
    ellipsoid.SetUserMatrix(rm)
    ellipsoid.GetProperty().SetDiffuseColor(1, 1, 1)
    ellipsoid.GetProperty().SetSpecular(.1)
    ellipsoid.GetProperty().SetSpecularPower(5)
    ellipsoid.GetProperty().SetOpacity(0.2)
    
    return ellipsoid, ellipsoidTextActor


def bacterialVolume(r):
    """
    Calculate the volume of all recorded bacteria.
    
    :@type r: int
    :@param r: The radius of the bacteria (the actor components)
    
    :@rtype: float
    :@return: The total volume of all recorded bacteria 
    """
    accumVol = 0.0
    cylvol = lambda pt1,pt2: math.pi*r**2*(pt1-pt2).length()
    spvol = (4.0/3)*math.pi*r**3
    
    for bact in DataStore.Bacteria():
        for i in range(len(bact.Markers)-1):
            accumVol += cylvol(bact.Markers[i], bact.Markers[i+1])
        accumVol += spvol
    
    return accumVol
    

def ellipsoidType(radius):
    tol = 0.5
    equiv = lambda x,y: y-tol < x < y+tol
    
    if equiv(radius.x, radius.y) and equiv(radius.y, radius.z):
        return "Sphere"
    elif equiv(radius.x, radius.y) and radius.y > radius.z:
        return "Oblate spheroid"
    elif equiv(radius.x, radius.y) and radius.y < radius.z:
        return "Prolate spheroid"
    
    return "Scalene ellipsoid"


def minimumVolumeEllipsoid(P, tol):
    """
    Finds the minimum volume enclosing ellipsoid (MVEE) of a set of data
    points stored in matrix P. The following optimization problem is solved: 
    
    minimize       log(det(A))
    subject to     (P_i - c)' * A * (P_i - c) <= 1
                   
    in variables A and c, where P_i is the i-th column of the matrix P. 
    The solver is based on Khachiyan Algorithm, and the final solution 
    is different from the optimal value by the pre-specified amount of 
    'tolerance'.
    
    Converted from original matlab code at: 
    http://www.mathworks.com/matlabcentral/fileexchange/9542-minimum-volume-enclosing-ellipsoid
    
    Author: Nima Moshtagh
    Email: nima@seas.upenn.edu
    
    :@type P: numpy.ndarray
    :@param P: (d x N) dimensional array containing N points in R^d.
    :@type tol: float
    :@param tol: Error in the solution with respect to the optimal value.
    
    :@rtype: tuple
    :@return: A: (d x d) matrix of the ellipse equation in the 'center form': 
                  (x-c)' * A * (x-c) = 1 
              c: 'd' dimensional vector as the center of the ellipse.
    """
    d, N = P.shape
    
    # Solving the dual problem
    Q = zeros((d+1,N))
    Q[0:d][:] = P[0:d][0:N]
    Q[d,:] = ones((1,N))
    
    cnt = 1
    err = 1
    u = (1.0/N) * ones((N,1))
    
    # Khachiyan Algorithm
    while err > tol:
        X = dot(dot(Q,diag(u[:,0])), Q.T)
        M = diag(dot(dot(Q.T, la.inv(X)), Q))
        (_,maximum),(_,j) = extents(M)
        step_size = (maximum - d -1)/((d+1)*(maximum-1))
        new_u = (1 - step_size) * u
        new_u[j] = new_u[j] + step_size
        cnt += 1
        err = la.norm(new_u - u)
        u = new_u
    
    # Finds the ellipse equation in the 'center form': 
    # (x-c)' * A * (x-c) = 1
    # It computes a dxd matrix 'A' and a d dimensional vector 'c' as the center
    # of the ellipse. 
    U = diag(u[:,0])
    A = (1.0/d) * la.inv(dot(dot(P,U),P.T) - dot(dot(P, u), dot(P, u).T))
    c = dot(P, u)
    
    return A, c

def extractEllipsoidParams(A):
    """
    Given a matrix ellipse equation in 'center' form, extract the radii 
    and the rotation matrix.
    
    :@type A: numpy.ndarray
    :@type param: 3x3 array representing the equation of an ellipsoid 
                  in 'center' form.
    :@rtype: tuple
    :@return: The radii (a,b,c) and the 3x3 rotation matrix to align 
              the ellipsoid on the proper axes. 
    """
    U, D, V = la.svd(A)
    D = diag(D)
    V = V.T
    
    # Find ellipsoid radii
    a = 1/sqrt(D[0,0])
    b = 1/sqrt(D[1,1])
    c = 1/sqrt(D[2,2])
    
    return (a,b,c), V














def singular(A):
    """
    Determines if a matrix is singular by testing for inversion.
    
    :@type A: numpy.ndarray
    :@param A: Input matrix
    
    :@rtype: bool
    :@return: True if A cannot be inverted. False otherwise.
    """
    try:
        la.inv(A)
    except la.LinAlgError:
        return True
    return False


from itertools import count, izip
from collections import namedtuple

Extent = namedtuple('Extent', 'min, max')

def fastSphere(actorRadius):
    points = DataStore.BacteriaMarkers()
    
    # min/max for all components
    extX, idxX = extents(points[0])
    extY, idxY = extents(points[1])
    extZ, idxZ = extents(points[2])
    
    dVx = Vec3f(points[0][idxX.max], points[1][idxX.max], points[2][idxX.max]) - Vec3f(points[0][idxX.min], points[1][idxX.min], points[2][idxX.min])
    dVy = Vec3f(points[0][idxX.max], points[1][idxX.max], points[2][idxX.max]) - Vec3f(points[0][idxX.min], points[1][idxX.min], points[2][idxX.min])
    dVz = Vec3f(points[0][idxX.max], points[1][idxX.max], points[2][idxX.max]) - Vec3f(points[0][idxX.min], points[1][idxX.min], points[2][idxX.min])
    dx2 = dVx.dot(dVx)
    dy2 = dVy.dot(dVy)
    dz2 = dVz.dot(dVz)
    
    mdd = max(izip([dx2,dy2,dz2], count()))[1]  # maximum distance dimension
    dlist = [dVx, dVy, dVz]
    idxlist = [idxX, idxY, idxZ]
    # Center = midpoint of extremes
    C = Vec3f(points[0][idxlist[mdd].min], points[1][idxlist[mdd].min], points[2][idxlist[mdd].min]) + (dlist[mdd] / 2.0)
    # radius squared: max point in dimension mdd - Center 
    rad2 = Vec3f(points[0][idxlist[mdd].max], points[1][idxlist[mdd].max], points[2][idxlist[mdd].max]) - C
    rad2 = rad2.dot(rad2)
    radius = sqrt(rad2)
    
    # now check that all points V[i] are in the ball
    # and if not, expand the ball just enough to include them
    for i in range(points[0]):
        dV = Vec3f(points[0][i], points[1][i], points[2][i]) - C
        dist2 = dV.dot(dV)
        if dist2 <= rad2:    # the point is inside the ball already
            continue
        # point not in ball, so expand ball to include it
        dist = sqrt(dist2)
        radius = (radius + dist) / 2.0   # enlarge radius just enough
        rad2 = radius**2
        C = C + ((dist-radius)/dist) * dV   # shift Center toward V[i] 
    
    volume = 4.0/3.0 * math.pi * radius**3
    
    sphere = createSphere(radius, C)
    sphere.GetProperty().SetDiffuseColor(1, 1, 1)
    sphere.GetProperty().SetSpecular(.1)
    sphere.GetProperty().SetSpecularPower(5)
    sphere.GetProperty().SetOpacity(0.2)
    
    sTextMapper = vtk.vtkTextMapper()
    sTextMapper.SetInput("Volume: %d\nRadius: %d" % (volume, radius))
    sTextMapper.GetTextProperty().SetJustificationToCentered()
    sTextMapper.GetTextProperty().SetVerticalJustificationToCentered()
    sTextMapper.GetTextProperty().SetColor(0.75, 0.75, 0.75)
    sTextMapper.GetTextProperty().SetFontSize(14)
    sTextActor = vtk.vtkActor2D() 
    sTextActor.SetMapper(sTextMapper)    
    sTextActor.GetPositionCoordinate().SetCoordinateSystemToWorld()
    sTextActor.GetPositionCoordinate().SetValue(C.x-30, C.y-30, C.z)
    
    return sphere, sTextActor
    
    

def extents(points):
    """"min/max for values in points and the indices of each"""
    (vmin, imin), (vmax, imax) = min(izip(points, count())), max(izip(points, count()))
    ext = Extent(vmin, vmax)
    idx = Extent(imin, imax)
    return ext, idx