'''
Created on Jul 24, 2011

@author: shareef
'''
from render.basic import createEllipsoid, createSphere
from store import DataStore
from vector import Vec3f

from numpy import *
import numpy.linalg as la
import vtk

HFF = 2.86

def fitEllipsoid(ds, actorRadius, mve=False):
    """
    Fit an ellipsoid to the existing recorded bacteria for estimation 
    of volume and shape.
    
    :@type ds: Vec3f 
    :@param ds: Data spacing. The ratio of microns/pixel
    :@type actorRadius: float
    :@param actorRadius: The radius of the recorded bacteria
    :@type mve: bool
    :@param mve: A flag indicating whether to use the MinimumVolumeEllipsoid 
                 or the Lowner method for fitting.
    
    :@rtype: tuple -> (vtkActor, vtkActor)
    :@return: parametric ellipsoid actor and text actor displaying the volume
    """
    points = [[],[],[]]
    fBacteria = False
    
    for bact in DataStore.Bacteria():
        points[0].extend([marker.x for marker in bact.Markers])
        points[1].extend([marker.y for marker in bact.Markers])
        points[2].extend([marker.z for marker in bact.Markers])
        
    # if no recorded bacteria, use the placed markers
    if not points[0]:
        for marker in DataStore.Markers():
            pt = Vec3f(marker.GetCenter())
            points[0].append(pt.x)
            points[1].append(pt.y)
            points[2].append(pt.z)
    else:
        fBacteria = True
    
    if not points[0] or len(points[0]) < 9:
        raise RuntimeError('At least 9 markers are needed to fit an ellipsoid')
    
    
    # output data to file
#    with open('ellipse.csv', 'w') as e:
#        writer = csv.writer(e, delimiter=',')
#        writer.writerows(points)
    
    points = array(points)
    
    fpoints = 2.8 * points
    
    if mve:
        print 'fitting MVE'
        A, center = minimumVolumeEllipsoid(points, tol=0.001)
        fA, fcenter = lownerEllipsoid(fpoints, tol=0.001)
    else:
        print 'fitting Lowner'
        A, center = lownerEllipsoid(points, tol=0.001)
        fA, fcenter = lownerEllipsoid(fpoints, tol=0.001)
    
    r, RM   = extractEllipsoidParams(A)
    fr, fRM = extractEllipsoidParams(fA)
    radius = Vec3f(r)
    fradius = Vec3f(fr)
    
    center = Vec3f(list(center[:,0]))
    
    print str(ds)
    volume = 4.0/3.0 * math.pi * fradius.x * fradius.y * fradius.z * ds.x * ds.y * ds.z
    
    bactVol = bacterialVolume() * ds.x * ds.y * ds.z if fBacteria else 0
    
    ibcDensity = bactVol/volume
    
    rm = vtk.vtkMatrix4x4()
    rm.DeepCopy((RM[0,0], RM[0,1], RM[0,2], center.x,
                 RM[1,0], RM[1,1], RM[1,2], center.y,
                 RM[2,0], RM[2,1], RM[2,2], center.z,
                    0   ,    0   ,    0   , 1))
    
    # make the ellipsoid cover the whole actor since it is fit using the centers
    radius += actorRadius
    
    out = []
    out.append("Ellipsoid type:\t%s" % ellipsoidType(fradius))
    out.append("Ellipsoid radii:\t%s" % str(fradius))
    out.append("Ellipsoid Volume:\t%f" % volume)
    if fBacteria:
        out.append("Bacteria Volume:\t%f" % bactVol)
        out.append("Bacterial Mass to Ellipsoid Volume ratio:\t%f" % ibcDensity)
    
    ellipsoid = createEllipsoid(radius, Vec3f())
    ellipsoid.SetUserMatrix(rm)
    ellipsoid.GetProperty().SetDiffuseColor(1, 1, 1)
    ellipsoid.GetProperty().SetSpecular(.1)
    ellipsoid.GetProperty().SetSpecularPower(5)
    ellipsoid.GetProperty().SetOpacity(0.2)
    
    return ellipsoid, '\n'.join(out)


def bacterialVolume():
    """
    Calculate the volume of all recorded bacteria.
    Assumes invariant actor radius to assure comparable volumes 
    
    :@rtype: float
    :@return: The total volume of all recorded bacteria 
    """
    accumVol = 0.0
    r = 1
    cylvol = lambda pt1,pt2: (math.pi)*(r**2)*(pt1-pt2).length()
    spvol = (4.0/3) * math.pi * r**3
    
    for bact in DataStore.Bacteria():
        for i in range(len(bact.Markers)-1):
#            v = cylvol(convert(bact.Markers[i], ds), 
#                       convert(bact.Markers[i+1], ds))
#            l = (HFF*bact.Markers[i] - HFF*bact.Markers[i+1]).length()
            tmp = cylvol(HFF*bact.Markers[i], HFF*bact.Markers[i+1])
#            print "cylvol: ", tmp, str(l)
            accumVol += tmp
        accumVol += spvol
    
    return accumVol

def convert(pt, ds):
    return Vec3f(pt.x*ds.x, pt.y*ds.y, pt.z*ds.z)
    

def ellipsoidType(radius):
    tol = 10
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


def lownerEllipsoid(P, tol):
    """
    Finds an approximation of the Lowner ellipsoid
    of the points in the columns of P.  The resulting ellipsoid satisfies
    
        x=A-repmat(C,size(A,2)); all(dot(x,E*x)<=1)
    
    and has a volume of approximately (1+tol) times the minimum volume
    ellipsoid satisfying the above requirement.
    
    A must be real and non-degenerate. tol must be positive.
    
    Reference:
        Khachiyan, Leonid G.  Rounding of Polytopes in the Real Number
            Model of Computation.  Mathematics of Operations Research,
            Vol. 21, No. 2 (May, 1996) pp. 307--320.
            
    Note: converted to python from Matlab implemetation by Anye Li
    http://www.mathworks.com/matlabcentral/fileexchange/21930
    
    This method is slightly faster than minimumVolumeEllipsoid().
    
    :@type P: numpy.ndarray
    :@param P: (d x N) dimensional array containing N points in R^d.
    :@type tol: float
    :@param tol: Error in the solution with respect to the optimal value.
    
    :@rtype: tuple
    :@return: A: (d x d) matrix of the ellipse equation in the 'center form': 
                  (x-c)' * A * (x-c) = 1 
              c: 'd' dimensional vector as the center of the ellipse.
    """
    n, m = P.shape
    if n < 1:
        raise Exception("P must be of at least 1 dimension")
    
    # Find the Lowner ellipsoid of the centrally symmetric set lifted
    # to a hyperplane in a higher dimension.
    F = khachiyan(vstack((P, ones((1,m)))), tol)
    # Intersect with the hyperplane where the input points lie.
    A = F[0:n][:,0:n]
    b = F[-1][0:n][:,newaxis]
    c = la.solve(-A,b)
    E = A/(1-dot(c[:,0].T,b-F[-1][-1])[0])
    
    # Force all the points to really be covered.
    ac = P - tile(c, (1,m))
    E = E/max(bdot(ac,dot(E,ac)))

    return E, c

def khachiyan(a, tol):
    n, m = a.shape
    # Initialize the barycentric coordinate descent.
    invA = m * la.inv(dot(a, a.T))
    w = bdot(a, dot(invA, a))
    
    # Khachiyan's BCD algorithm for finding the Lowner ellipsoid of a
    # centrally symmetric set.
    while True:
        (_, w_r), (_, r) = extents(w)
        f = w_r / n
        epsilon = f - 1
        if epsilon <= tol: 
            break
        g = epsilon / ((n - 1) * f)
        h = 1 + g 
        g = g / f
        b = dot(invA, a[:, r])
        invA = h * invA - g * b[:, newaxis] * b
        bTa = dot(b, a)
        w = h * w - g * (bTa * bTa)
    
    return invA / max(bdot(a, dot(invA, a)))



def bdot(a, b):
    """
    Treat two n x m arrays as hstacked column vectors
    and broadcast the dot product over each of the m columns.
    
    :@type a,b: numpy.ndarray
    :@param a,b: An n x m array 
    :@rtype: numpy.ndarray
    :@return: An array of size 1 x m containing the scalar results 
              of m dot products between each column of a and b.
    """
    _, m = a.shape 
    return array([dot(a[:,i],b[:,i]) for i in range(m)])
    

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