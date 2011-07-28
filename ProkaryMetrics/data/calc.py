'''
Created on May 25, 2011

@author: dabdoubs
'''
from render.basic import createEllipsoid
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
    dataRange = [[],[],[]]
    
    for bact in DataStore.Bacteria():
        dataRange[0].extend([marker.x for marker in bact.Markers])
        dataRange[1].extend([marker.y for marker in bact.Markers])
        dataRange[2].extend([marker.z for marker in bact.Markers])  
    
    # output data to file
    with open('ellipse.csv', 'w') as e:
        writer = csv.writer(e, delimiter=',')
        writer.writerows(dataRange)
    
    
    
    
    radius = Vec3f((max(dataRange[0]) - min(dataRange[0]))/2,
                   (max(dataRange[1]) - min(dataRange[1]))/2,
                   (max(dataRange[2]) - min(dataRange[2]))/2)
    
    centerAvg = Vec3f(average(dataRange[0]),
                   average(dataRange[1]),
                   average(dataRange[2]))
    
    centerMed = Vec3f(median(dataRange[0]),
                   median(dataRange[1]),
                   median(dataRange[2]))
    
    center = centerAvg
    
    volume = 4.0/3.0 * math.pi * radius.x * radius.y * radius.z
    bactVol = bacterialVolume(actorRadius)
    
    ibcDensity = bactVol/volume
    
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
    print "Ellipsoid center(avg): ", str(centerAvg)
    print "Ellipsoid center(median): ", str(centerMed)
    print "Ellipsoid Volume: ", volume
    print "Bacteria Volume: ", bactVol
    print "Bacterial Mass to Ellipsoid Volume ratio: ", ibcDensity
    
    ellipsoid = createEllipsoid(radius, center)
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


FIT_FLAG_ARBITRARY = 0
FIT_FLAG_3_AXES = 1
FIT_FLAG_2_AXES = 2
FIT_FLAG_SPHERE = 3

def ellipsoid_fit(points, flag=FIT_FLAG_ARBITRARY, axes=None):
    """
    Fit an ellipsoid to a set of xyz data points.
    
    :@type points: numpy.ndarray
    :@param points: An n x 3 array representing points in 3D space that the 
                    ellipsoid will be fit to.
    :@type flag: int
    :@param flag: Determine whether an aribtrary ellipsoid will be 
                  fit (default), an ellipsoid along axes given in 'points', 
                  an ellipsoid along two particular axes (indicated by 
                  parameter 'axes'), or with 3 equal axes (sphere).
    :@type axes: str 
    :@param axes: Indicates the two axes to make equivalent: 'xy', 'xz', 'yz'.
    
    :@rtype: tuple
    :@return: center -  ellispoid center coordinates [xc, yc, zc]
              radi   -  ellipsoid radii [a, b, c]
              evecs  -  ellipsoid radii directions as columns of the 3x3 array
              v      -  the 9 parameters describing the ellipsoid algebraically: 
                        Ax^2 + By^2 + Cz^2 + 2Dxy + 2Exz + 2Fyz + 2Gx + 2Hy + 2Iz = 1
    
    Note: Translated from Matlab file: ellipsoid_fit.m found at
          http://www.mathworks.com/matlabcentral/fileexchange/24693-ellipsoid-fit 
    Original Author: Yury Petrov, Northeastern University, Boston, MA
    """
    if points.shape[0] < 3:
        raise Exception('points must be an array of dimension n x 3')
    
    x = points[:,0][:,newaxis]
    y = points[:,1][:,newaxis]
    z = points[:,2][:,newaxis]
    
    # need min number of data points
    if len(x) < 9 and flag == FIT_FLAG_ARBITRARY: 
        raise Exception('Must have at least 9 points to fit a unique ellipsoid')
    if len(x) < 6 and flag == FIT_FLAG_3_AXES:
        raise Exception('Must have at least 6 points to fit a unique oriented ellipsoid')
    if len(x) < 5 and flag == FIT_FLAG_2_AXES:
        raise Exception('Must have at least 5 points to fit a unique oriented ellipsoid with two axes equal')
    if len(x) < 3 and flag == FIT_FLAG_SPHERE:
        raise Exception('Must have at least 4 points to fit a unique sphere')
    
    # fit ellipsoid in the form Ax^2 + By^2 + Cz^2 + 2Dxy + 2Exz + 2Fyz + 2Gx + 2Hy + 2Iz = 1
    if flag == FIT_FLAG_ARBITRARY:
        D = hstack([ x * x,
                     y * y,
                     z * z,
                     2 * x * y,
                     2 * x * z,
                     2 * y * z,
                     2 * x,
                     2 * y, 
                     2 * z ])  # n x 9 ellipsoid parameters
    
    # fit ellipsoid in the form Ax^2 + By^2 + Cz^2 + 2Gx + 2Hy + 2Iz = 1
    elif flag == FIT_FLAG_3_AXES:
        D = hstack([ x * x,
                     y * y,
                     z * z,
                     2 * x,
                     2 * y, 
                     2 * z ])  # n x 6 ellipsoid parameters
    
    # fit ellipsoid in the form Ax^2 + By^2 + Cz^2 + 2Gx + 2Hy + 2Iz = 1,
    # where A = B or B = C or A = C
    elif flag == FIT_FLAG_2_AXES:
        if axes == 'yz' or axes == 'zy':
            D = hstack([ y * y + z * z,
                         x * x,
                         2 * x,
                         2 * y,
                         2 * z ])
        elif axes == 'xz' or axes == 'zx':
            D = hstack([x * x + z * z,
                        y * y,
                        2 * x,
                        2 * y,
                        2 * z ])
        else:
            D = hstack([x * x + y * y,
                        z * z,
                        2 * x,
                        2 * y,
                        2 * z ])
    
    # fit sphere in the form A(x^2 + y^2 + z^2) + 2Gx + 2Hy + 2Iz = 1
    else:
        D = hstack([x * x + y * y + z * z,
                    2 * x,
                    2 * y, 
                    2 * z ])  # ndatapoints x 4 sphere parameters
    
    # solve the normal system of equations: vD = B where B is a colvec of 1
    if D.shape[0] == D.shape[1] or not singular(D):
        v, res, rank, s = la.solve(D, ones((x.shape[0], 1)))
    else:
        v, res, rank, s = la.lstsq(D, ones((x.shape[0], 1)))

    # convert back to row vector to enable v[i] access
    v = hstack(v)
    # find the ellipsoid parameters
    if flag == FIT_FLAG_ARBITRARY:
        # form the algebraic form of the ellipsoid
        # Ax^2 + B   y^2 + Cz^2 + 2Dxy + 2Exz + 2Fyz + 2Gx + 2Hy + 2Iz   -1 = 0
        # v(1)   v(2)      v(3)    v(4)   v(5)   v(6)   v(7)  v(8)  v(9)
        A = array([[v[0], v[3], v[4], v[6]],
                   [v[3], v[1], v[5], v[7]],
                   [v[4], v[5], v[2], v[8]],
                   [v[6], v[7], v[8],  -1 ]])
        # find the center of the ellipsoid
        center = la.solve(-A[0:3][:,0:3], array([[v[6]], [v[7]], [v[8]]]))
        # form the corresponding translation matrix
        T = eye(4)
        #TODO: check this array access
        T[3][0:3] = hstack(center)
        # translate to the center
        R = mat(T) * mat(A) * mat(T.T)
        # find the axes and radii of the ellipsoid
        evals, evecs = la.eig(R[0:3][:,0:3]/-R[3,3])
        radii = emath.sqrt(1 / evals)
    else:
        if flag == FIT_FLAG_3_AXES:
            v = array([v[0], v[1], v[2], 0, 0, 0, v[3], v[4], v[5]])
        elif flag == FIT_FLAG_2_AXES:
            if axes == 'xz' or axes == 'zx':
                v = array([v[0], v[1], v[0], 0, 0, 0, v[2], v[3], v[4]])
            elif axes == 'yz' or axes == 'zy':
                v = array([v[1], v[0], v[0], 0, 0, 0, v[2], v[3], v[4]])
            else: # xy
                v = array([v[0], v[0], v[1], 0, 0, 0, v[2], v[3], v[4]])
        else:
            v = array([v[0], v[0], v[0], 0, 0, 0, v[1], v[2], v[3]])

        center = hstack(-v[6:9] / v[0:3])
        gam = 1 + v[6]**2 / v[0] + v[7]**2 / v[1] + v[8]**2 / v[2]
        radii = hstack(sqrt(float(gam) / v[0:3]))
        evecs = eye(3)
        
    return center, radii, evecs, v


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






























