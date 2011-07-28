from vtk import *

# Demonstrate how to extract polygonal cells with an implicit function
# get the interactor ui

# create a sphere source and actor
#
sphere = vtkSphereSource()
sphere.SetThetaResolution(8)
sphere.SetPhiResolution(16)
sphere.SetRadius(1.5)

# Extraction stuff
t = vtkTransform()
t.RotateX(90)
cylfunc = vtkCylinder()
cylfunc.SetRadius(0.5)
cylfunc.SetTransform(t)
extract = vtkExtractPolyDataGeometry()
extract.SetInputConnection(sphere.GetOutputPort())
extract.SetImplicitFunction(cylfunc)
extract.ExtractBoundaryCellsOn()
extract.ExtractInsideOff()

sphereMapper = vtkPolyDataMapper()
sphereMapper.SetInputConnection(extract.GetOutputPort())
sphereMapper.GlobalImmediateModeRenderingOn()

sphereActor = vtkActor()
sphereActor.SetMapper(sphereMapper)

# Create the RenderWindow, Renderer and both Actors
#
ren1 = vtk.vtkRenderer()
renWin = vtk.vtkRenderWindow()
renWin.AddRenderer(ren1)
iren = vtk.vtkRenderWindowInteractor()
iren.SetRenderWindow(renWin)

# Add the actors to the renderer, set the background and size
#
ren1.AddActor(sphereActor)

ren1.ResetCamera()
ren1.GetActiveCamera().Azimuth(30)

ren1.SetBackground(0.1, 0.2, 0.4)
renWin.SetSize(300, 300)
iren.Initialize()
renWin.Render()
iren.Start()

