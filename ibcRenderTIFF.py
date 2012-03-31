import math
import enthought.tvtk.pyface.ui.wx as enWX
import sys
import vtk

ren = None
iren = None
renWin = None
picker = None
redCone = None
greenCone = None

def initRenderer():
    """
    Create the renderer, the render window, and the interactor. The renderer
    draws into the render window, the interactor enables mouse- and 
    keyboard-based interaction with the scene.
    """
    global ren, renWin, iren
    ren = vtk.vtkRenderer()
    ren.SetBackground(0, 0, 0)
    
    renWin = vtk.vtkRenderWindow()
    renWin.SetSize(800, 600)
    renWin.AddRenderer( ren )

    # render window interactor
    iren = vtk.vtkRenderWindowInteractor()
    iren.SetRenderWindow( renWin )

def renderIBC(filePrefix, imgLow, imgHigh):
    global picker, redCone, greenCone
    #
    # This example reads a volume dataset, extracts an isosurface that
    # represents the skin and displays it.
    #
    
    
    # The following reader is used to read a series of 2D slices (images)
    # that compose the volume. The slice dimensions are set, and the
    # pixel spacing. The data Endianness must also be specified. The reader
    # usese the FilePrefix in combination with the slice number to construct
    # filenames using the format FilePrefix.%d. (In this case the FilePrefix
    # is the root name of the file: quarter.)
    #vtkVolume16Reader v13R
    #  v13R SetDataDimensions 1388 1040
    #  v13R SetDataByteOrderToBigEndian 
    #  v13R SetFilePrefix  "IBC146h.R_s"
    #  v13R SetImageRange 0  44
    #  v13R SetDataSpacing  1 1 2
      
    # Image reader
    v13G = vtk.vtkTIFFReader()
    v13G.SetDataExtent(1, 1380, 1, 1030, imgLow, imgHigh)
    v13G.SetDataByteOrderToLittleEndian() 
    v13G.SetFilePrefix(filePrefix)
    v13G.SetDataSpacing(0.1, 0.1, 0.6)
    
    # Gaussian Smoothing
    gaus_v13G = vtk.vtkImageGaussianSmooth()
    gaus_v13G.SetDimensionality(3)
    gaus_v13G.SetStandardDeviation(1)
    gaus_v13G.SetRadiusFactors(1, 1, 1)
    gaus_v13G.SetInput(v13G.GetOutput())
    
    
    # Set up the volume rendering
    volumeMapper = vtk.vtkVolumeTextureMapper3D()
    volumeMapper.SetInput(v13G.GetOutput())
    
    volume = vtk.vtkVolume()
    volume.SetMapper(volumeMapper)
    
    
    # Surface rendering
    bactExtractor = vtk.vtkMarchingCubes()
    bactExtractor.SetInputConnection(gaus_v13G.GetOutputPort())
    bactExtractor.SetValue(0,20000)
    
#    bactNormals = vtk.vtkPolyDataNormals()
#    bactNormals.SetInputConnection(bactExtractor.GetOutputPort())
#    bactNormals.SetFeatureAngle(90.0)
#    
#    bactStripper = vtk.vtkStripper()
#    bactStripper.SetInputConnection(bactNormals.GetOutputPort())
#    
    bactLocator = vtk.vtkCellLocator()
    bactLocator.SetDataSet(bactExtractor.GetOutput())
    bactLocator.LazyEvaluationOn()
#    
#    bactMapper = vtk.vtkPolyDataMapper()
#    bactMapper.SetInputConnection(bactStripper.GetOutputPort())
#    bactMapper.ScalarVisibilityOff()
    
    
#    skinE_v13G = vtk.vtkContourFilter()
##    skinE_v13G = vtk.vtkMarchingCubes()
#    skinE_v13G.UseScalarTreeOn()
#    skinE_v13G.SetInput(gaus_v13G.GetOutput())
#    skinE_v13G.SetValue(0, 10000)
#    
    smooth_v13G = vtk.vtkSmoothPolyDataFilter()
    smooth_v13G.SetInput(bactExtractor.GetOutput())
    smooth_v13G.SetNumberOfIterations(50)
    
    deci_v13G = vtk.vtkDecimatePro()
    deci_v13G.SetInput(smooth_v13G.GetOutput())
    deci_v13G.SetTargetReduction(0.5)
    deci_v13G.PreserveTopologyOn()
    
    smoother_v13G = vtk.vtkSmoothPolyDataFilter()
    smoother_v13G.SetInput(deci_v13G.GetOutput())
    smoother_v13G.SetNumberOfIterations(50)
    
    skinNormals_v13G = vtk.vtkPolyDataNormals()
    skinNormals_v13G.SetInput(deci_v13G.GetOutput())
    skinNormals_v13G.SetFeatureAngle(60.0)
    
    
    skinStripper_v13G = vtk.vtkStripper()
    skinStripper_v13G.SetInput(skinNormals_v13G.GetOutput())
    
    
    skinMapper_v13G = vtk.vtkPolyDataMapper()
    skinMapper_v13G.SetInput(skinStripper_v13G.GetOutput())
    skinMapper_v13G.ScalarVisibilityOff()
    
    skin_v13G = vtk.vtkActor()
    skin_v13G.SetMapper(skinMapper_v13G)
    skin_v13G.GetProperty().SetDiffuseColor(0.2, 1, 0.2)
    skin_v13G.GetProperty().SetSpecular(.1)
    skin_v13G.GetProperty().SetSpecularPower(5)
    skin_v13G.GetProperty().SetOpacity(0.9)
    
    
    # It is convenient to create an initial view of the data. The FocalPoint
    # and Position form a vector direction. Later on (ResetCamera() method)
    # this vector is used to position the camera to look at the data in
    # this direction.
    aCamera = vtk.vtkCamera()
    aCamera.SetViewUp(0, 0, -1)
    aCamera.SetPosition(0, 1.1, 2)
    aCamera.SetFocalPoint(0, -0.25, 0)
    aCamera.ComputeViewPlaneNormal()
    
    
    
    # Actors are added to the renderer. An initial camera view is created.
    # The Dolly() method moves the camera towards the FocalPoint,
    # thereby enlarging the image.
    #aRenderer AddActor skin_v13R
    ren.AddActor(skin_v13G)
    ren.SetActiveCamera(aCamera)
    ren.ResetCamera() 
    aCamera.Dolly(1.0)
   
    
    # Note that when camera movement occurs (as it does in the Dolly()
    # method), the clipping planes often need adjusting. Clipping planes
    # consist of two planes: near and far along the view direction. The 
    # near plane clips out objects in front of the plane the far plane
    # clips out objects behind the plane. This way only what is drawn
    # between the planes is actually rendered.
    ren.ResetCameraClippingRange()
    
    
    # render
    renWin.Render()
    
    # CONE PICKER RENDER
    
    #---------------------------------------------------------
    # the cone points along the -x axis
    coneSource = vtk.vtkConeSource()
    coneSource.CappingOn()
    coneSource.SetHeight(2)
    coneSource.SetRadius(1)
    coneSource.SetResolution(11)
    coneSource.SetCenter(1,0,0)
    coneSource.SetDirection(-1,0,0)
    
    coneMapper = vtk.vtkDataSetMapper()
    coneMapper.SetInputConnection(coneSource.GetOutputPort())
    
    redCone = vtk.vtkActor()
    redCone.PickableOff()
    redCone.SetMapper(coneMapper)
    redCone.GetProperty().SetColor(1,0,0)
    
    greenCone = vtk.vtkActor()
    greenCone.PickableOff()
    greenCone.SetMapper(coneMapper)
    greenCone.GetProperty().SetColor(0,1,0)
    
    # Add the two cones (or just one, if you want)
    ren.AddViewProp(redCone)
    ren.AddViewProp(greenCone)
    
    #---------------------------------------------------------
    # the picker
    picker = vtk.vtkVolumePicker()
    picker.SetTolerance(1e-6)
    picker.SetVolumeOpacityIsovalue(0.1)
    # locator is optional, but improves performance for large polydata
    picker.AddLocator(bactLocator)
    
    #---------------------------------------------------------
    # custom interaction
    iren.AddObserver("MouseMoveEvent", MoveCursor)

    
    # END CONE PICKER RENDER
    
    # initialize and start the interactor
    iren.Initialize()
    iren.Start()
    

# A function to point an actor along a vector
def PointCone(actor,nx,ny,nz):
    actor.SetOrientation(0.0, 0.0, 0.0)
    n = math.sqrt(nx**2 + ny**2 + nz**2)
    if (nx < 0.0):
        actor.RotateWXYZ(180, 0, 1, 0)
        n = -n
    actor.RotateWXYZ(180, (nx+n)*0.5, ny*0.5, nz*0.5)

# A function to move the cursor with the mouse
def MoveCursor(iren,event=""):
    renWin.HideCursor()
    x,y = iren.GetEventPosition()
    picker.Pick(x, y, 0, ren)
    p = picker.GetPickPosition()
    n = picker.GetPickNormal()
    redCone.SetPosition(p[0],p[1],p[2])
    PointCone(redCone,n[0],n[1],n[2])
    greenCone.SetPosition(p[0],p[1],p[2])
    PointCone(greenCone,-n[0],-n[1],-n[2])
    iren.Render()


def main():
    if (len(sys.argv) < 4):
        print "Usage: python ibcRenderTIFF.py filePrefix imgLow imgHigh"
        sys.exit(1)
    
    initRenderer()
    renderIBC(sys.argv[1], int(sys.argv[2]), int(sys.argv[3]))

if __name__ == "__main__":
    sys.exit(main())
    
    
    
    
    
    
    
    
    
    
    
    
    
    