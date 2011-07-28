#http://www.vtk.org/pipermail/vtkusers/2003-October/069969.html

import vtk

numberOfInputPoints = 3

aSplineX = vtk.vtkCardinalSpline()
aSplineY = vtk.vtkCardinalSpline()
aSplineZ = vtk.vtkCardinalSpline()

inputPoints = vtk.vtkPoints()

aSplineX.AddPoint(0, 0)
aSplineY.AddPoint(0, 0)
aSplineZ.AddPoint(0, 0)
inputPoints.InsertPoint(0, 0, 0, 0)

aSplineX.AddPoint(1, 1)
aSplineY.AddPoint(1, 1)
aSplineZ.AddPoint(1, 0)
inputPoints.InsertPoint(1, 1, 1, 0)

aSplineX.AddPoint(2, 2)
aSplineY.AddPoint(2, 4)
aSplineZ.AddPoint(2, 0)
inputPoints.InsertPoint(2, 2, 4, 0)


# Generate the polyline for the spline.
points = vtk.vtkPoints()
profileData = vtk.vtkPolyData()
scalars = vtk.vtkFloatArray()

# Number of points on the spline
numberOfOutputPoints = 40

# Interpolate x, y and z by using the three spline filters and
# create new points
for i in range(numberOfOutputPoints):
    t = (numberOfInputPoints-1.0)/(numberOfOutputPoints-1.0)*i
    points.InsertPoint(i, aSplineX.Evaluate(t), aSplineY.Evaluate(t),
                       aSplineZ.Evaluate(t))
    scalars.InsertTuple1(i,t)

# Create the polyline.
lines = vtk.vtkCellArray()
lines.InsertNextCell(numberOfOutputPoints)
for i in range(numberOfOutputPoints):
    lines.InsertCellPoint(i)
 
profileData.SetPoints(points)
profileData.SetLines(lines)
profileData.GetPointData().SetScalars(scalars)

# Add thickness to the resulting line.
profileTubes = vtk.vtkTubeFilter()
profileTubes.SetNumberOfSides(8)
profileTubes.SetInput(profileData)
profileTubes.SetRadius(.01)

# Vary tube thickness with scalar
profileTubes.SetRadiusFactor(20)
profileTubes.SetVaryRadiusToVaryRadiusByScalar()  

profileMapper = vtk.vtkPolyDataMapper()
profileMapper.SetInput(profileTubes.GetOutput())
profileMapper.SetScalarRange(0,t)   

#Set this to Off to turn off color variation with scalar
profileMapper.ScalarVisibilityOn()

profile = vtk.vtkActor()
profile.SetMapper(profileMapper)
profile.GetProperty().SetSpecular(.3)
profile.GetProperty().SetSpecularPower(30)

# Now create the RenderWindow, Renderer and Interactor
ren = vtk.vtkRenderer()
renWin = vtk.vtkRenderWindow()
renWin.AddRenderer(ren)

iren = vtk.vtkRenderWindowInteractor()
iren.SetRenderWindow(renWin)

# Add the actors
ren.AddActor(profile)

renWin.SetSize(500, 500)

iren.Initialize()
renWin.Render()
iren.Start()