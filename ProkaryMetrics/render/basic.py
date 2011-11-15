'''
Created on Jan 6, 2011

@author: shareef
'''
from store import DataStore
from vector import Vec3f
import wx
import vtk

boolInt = lambda v: 1 if v else 0

class Color(object):
    def __init__(self, rgb=(1,1,1)):
        if not isinstance(rgb, tuple) and not isinstance(rgb, list):
            raise TypeError("Color instantiation requires tuple or list")
        if len(rgb) != 3:
            raise TypeError("Color instantiation requires tuple or list of size 3")
        
        self.r = rgb[0]
        self.g = rgb[1]
        self.b = rgb[2]
        
    def __str__(self):
        return '(%f, %f, %f)' % (self.r, self.g, self.b)
  
    def __repr__(self):
        return '(%f, %f, %f)' % (self.r, self.g, self.b)
    
    def __eq__(self, other):
        return self.r == other.r and self.g == other.g and self.b == other.b
    
    def __ne__(self, other):
        #return self.r != other.r or self.g != other.g or self.b != other.b
        return self.toTuple() != other.toTuple()
    
    def toTuple(self):
        return self.r, self.g, self.b
    
    def toWX(self):
        return wx.Colour(int(255*self.r), int(255*self.g), int(255*self.b))
    
    @classmethod
    def fromWX(cls, rgb):
        """
        Creates a valid Color object with fractional (0-1) rgb values
        
        :@type rgb: tuple
        :@param rgb: RGB values in the range 0-255.
        
        :@rtype: render.basic.Color
        :@return: A Color with appropriate values.   
        """
        return Color((rgb[0]/255.0, rgb[1]/255.0, rgb[2]/255.0))



#RedColor = Color((1.0, 0.2, 0.2))
#GreenColor = Color((0.2, 1.0, 0.2))
#BlueColor = Color((0.2, 0.2, 1.0))
WhiteColor = Color((1.0, 1.0, 1.0))
IBCColor = Color((0, 0.76, 0.063))
BacteriaColor = Color((1.0, 0.57, 0))
MarkerColor = Color((1.0, 0.0, 0.0))
    

def createEllipsoid(radius, center):
    """
    Create a parametric ellipsoid with the given values.
    
    :@type radius: Vec3d
    :@param radius: The 3D radius of the ellipsoid
    :@type center: Vec3D
    :@param center: The center of the ellipsoid
    
    :@rtype: vtk.vtkActor
    :@return: An actor mapped from a parametric ellipsoid source 
    """
    tol = 0
    # set up the source
    ellipsoid = vtk.vtkParametricEllipsoid()
    ellipsoid.SetXRadius(radius.x+tol)
    ellipsoid.SetYRadius(radius.y+tol)
    ellipsoid.SetZRadius(radius.z+tol)
    ellipsoidSource = vtk.vtkParametricFunctionSource()
    ellipsoidSource.SetParametricFunction(ellipsoid)

    # mapper and actor
    ellipsoidMapper = vtk.vtkPolyDataMapper()
    ellipsoidMapper.SetInputConnection(ellipsoidSource.GetOutputPort())
    
    ellipsoidActor = vtk.vtkActor()
    ellipsoidActor.SetMapper(ellipsoidMapper)
    ellipsoidActor.SetPosition(center.x, center.y, center.z)

    return ellipsoidActor


def createSphere(radius, center):
    sphere = vtk.vtkSphereSource()
    sphere.SetCenter(center.x, center.y, center.z)
    sphere.SetRadius(radius)
    sphere.SetPhiResolution(20)
    sphere.SetThetaResolution(20)
    
    sphereMapper = vtk.vtkPolyDataMapper()
    sphereMapper.SetInput(sphere.GetOutput())
    
    sphereActor = vtk.vtkActor()
    sphereActor.SetMapper(sphereMapper)
    
    return sphereActor


class RenderLayer(object):
    def __init__(self):
        pass
        

class ImageRenderer(object):
    def __init__(self):
        self.imageSetID = None
        self.imageArray = None
        
    def Render(self):
        pass
    
    @property
    def ImageSetID(self):
        return self.imageSetID
    
    #TODO: this should probably be moved into the data.imageIO.VolumeImageReader code
    def SetImageSet(self, id):
        self.imageSetID = id
        self.color = DataStore.GetImageSet(id).color
    
    @property
    def VolumeMapper(self):
        """
        This is necessary for the main render panel to assign clipping planes 
        to the rendered volume for use with interactive clipping.
        
        :@rtype: vtk.vtkAbstractMapper
        """
        pass



def generateSpline(markers):
    aSplineX = vtk.vtkCardinalSpline()
    aSplineY = vtk.vtkCardinalSpline()
    aSplineZ = vtk.vtkCardinalSpline()
    
    for i, marker in enumerate(markers):
        center = Vec3f(marker.GetCenter()) if not isinstance(marker, Vec3f) else marker
        aSplineX.AddPoint(i, center.x)
        aSplineY.AddPoint(i, center.y)
        aSplineZ.AddPoint(i, center.z)
    
    # Generate the polyline for the spline.
    points = vtk.vtkPoints()
    scalars = vtk.vtkFloatArray()
    
    # Number of points on the spline
    splineRes = len(markers)*1
    
    # Interpolate x, y and z by using the three spline filters and
    # create new points
    splineList = []
    for i in range(splineRes):
        t = (len(markers)-1.0)/(splineRes-1.0)*i
        splineList.append((aSplineX.Evaluate(t), aSplineY.Evaluate(t),
                           aSplineZ.Evaluate(t)))
        points.InsertPoint(i, splineList[-1][0], splineList[-1][1],
                           splineList[-1][2])
        scalars.InsertTuple1(i,t)
        
    return points, scalars, t, splineList
        
    