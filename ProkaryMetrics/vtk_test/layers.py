'''
Created on Apr 16, 2011

@author: shareef
'''
import vtk

def updateAxis(iren, event):
    cPos, cFoc, aFoc, size = [], [], [], []
    key = iren.GetKeyCode().upper()
    print key
    
    # set the axis camera according to the main renderer.
    cam = aRenderer.GetActiveCamera()
    cpos = cam.GetPosition()
    cFoc = cam.GetFocalPoint()
    aFoc = aAxisRenderer.GetActiveCamera().GetFocalPoint()
    aAxisRenderer.GetActiveCamera().SetViewUp(cam.GetViewUp())
    aAxisRenderer.GetActiveCamera().SetPosition(cPos[0] - cFoc[0] + aFoc[0],
                                                cPos[1] - cFoc[1] + aFoc[1],
                                                cPos[2] - cFoc[2] + aFoc[2])
    aAxisRenderer.ResetCamera()
    
    # keep the axis window size a constant 120 pixels squared (ugly).
    size = renWin.GetSize()
    aAxisRenderer.SetViewport((size[0]-120.0)/size[0], 0., 1., (120.0)/size[1])



renWin = vtk.vtkRenderWindow()
aAxisRenderer = vtk.vtkRenderer()
aRenderer = vtk.vtkRenderer()

#  create the renderer stuff
aRenderer.SetBackground(0,0,204)

aAxisRenderer = vtk.vtkRenderer()
aAxisRenderer.SetViewport(0.8,0,1,0.2)
aAxisRenderer.SetBackground(0,0,204)
aAxisRenderer.InteractiveOff()

renWin = vtk.vtkRenderWindow()
renWin.AddRenderer(aRenderer)
renWin.AddRenderer(aAxisRenderer)
renWin.SetSize(600,600)

iren = vtk.vtkRenderWindowInteractor()
iren.SetRenderWindow(renWin)

# make a sphere actor
sphere = vtk.vtkSphereSource()
sphere.SetPhiResolution(12)
sphere.SetThetaResolution(12)

colorIt = vtk.vtkElevationFilter()
colorIt.SetInput(sphere.GetOutput())
colorIt.SetLowPoint(0,0,-1)
colorIt.SetHighPoint(0,0,1)

sphereMapper = vtk.vtkDataSetMapper()
sphereMapper.SetInput(colorIt.GetOutput())

actor = vtk.vtkActor()
actor.SetMapper(sphereMapper)

# make the 3D axis
axisObj = vtk.vtkAxes()
axisObj.SetScaleFactor(1.0)

axisTube = vtk.vtkTubeFilter()
axisTube.SetInput(axisObj.GetOutput())
axisTube.SetRadius(1.0/20.)
axisTube.SetNumberOfSides(6)

axisMapper = vtk.vtkPolyDataMapper()
axisMapper.SetInput(axisTube.GetOutput())
axisMapper.ScalarVisibilityOff()

axis = vtk.vtkActor()
axis.SetMapper(axisMapper)
axis.PickableOff()
axis.GetProperty().SetColor(0,0,0)

# now, tell the main renderer our actors
aRenderer.AddActor(actor)
aAxisRenderer.AddActor(axis)

# callback command is set to watch the main renderer
iren.AddObserver("AnyEvent", updateAxis)

# start the interaction
iren.Initialize()
iren.Start()
    
    
    
    
    
    
    
    