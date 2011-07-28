'''
Created on May 25, 2011

@author: dabdoubs
'''
import vtk

# ------------------------------------------------------------
# Create a super ellipsoid
# ------------------------------------------------------------
superEllipsoid = vtk.vtkParametricSuperEllipsoid()
superEllipsoid.SetXRadius(1.25)
superEllipsoid.SetYRadius(1.5)
superEllipsoid.SetZRadius(1.0)
superEllipsoid.SetN1(1.1)
superEllipsoid.SetN2(1.75)

superEllipsoidSource = vtk.vtkParametricFunctionSource()
superEllipsoidSource.SetParametricFunction(superEllipsoid)
superEllipsoidSource.SetScalarModeToV()

superEllipsoidMapper = vtk.vtkPolyDataMapper()
superEllipsoidMapper.SetScalarRange(0, 3.14)
superEllipsoidMapper.SetInputConnection(superEllipsoidSource.GetOutputPort())

superEllipsoidActor = vtk.vtkActor()
superEllipsoidActor.SetMapper(superEllipsoidMapper)
superEllipsoidActor.SetPosition(8, 4, 0)

superEllipsoidTextMapper = vtk.vtkTextMapper()
superEllipsoidTextMapper.SetInput("Super Ellipsoid")
superEllipsoidTextMapper.GetTextProperty().SetJustificationToCentered()
superEllipsoidTextMapper.GetTextProperty().SetVerticalJustificationToCentered()
superEllipsoidTextMapper.GetTextProperty().SetColor(1, 0, 0)
superEllipsoidTextMapper.GetTextProperty().SetFontSize(14)
superEllipsoidTextActor = vtk.vtkActor2D()
superEllipsoidTextActor.SetMapper(superEllipsoidTextMapper)
superEllipsoidTextActor.GetPositionCoordinate().SetCoordinateSystemToWorld()
superEllipsoidTextActor.GetPositionCoordinate().SetValue(8, 1.5, 0)

# ------------------------------------------------------------
# Create an ellipsoidal surface
# ------------------------------------------------------------
ellipsoid = vtk.vtkParametricEllipsoid()
ellipsoid.SetXRadius(1)
ellipsoid.SetYRadius(0.75)
ellipsoid.SetZRadius(0.5)
ellipsoidSource = vtk.vtkParametricFunctionSource()
ellipsoidSource.SetParametricFunction(ellipsoid)
ellipsoidSource.SetScalarModeToZ()

ellipsoidMapper = vtk.vtkPolyDataMapper()
ellipsoidMapper.SetInputConnection(ellipsoidSource.GetOutputPort())
ellipsoidMapper.SetScalarRange(-0.5, 0.5)

ellipsoidActor = vtk.vtkActor()
ellipsoidActor.SetMapper(ellipsoidMapper)
ellipsoidActor.SetPosition(-1, -1, 0)
ellipsoidActor.SetScale(1.5, 1.5, 1.5)

ellipsoidTextMapper = vtk.vtkTextMapper()
ellipsoidTextMapper.SetInput("Ellipsoid")
ellipsoidTextMapper.GetTextProperty().SetJustificationToCentered()
ellipsoidTextMapper.GetTextProperty().SetVerticalJustificationToCentered()
ellipsoidTextMapper.GetTextProperty().SetColor(1, 0, 0)
ellipsoidTextMapper.GetTextProperty().SetFontSize(14)
ellipsoidTextActor = vtk.vtkActor2D() 
ellipsoidTextActor.SetMapper(ellipsoidTextMapper)    
ellipsoidTextActor.GetPositionCoordinate().SetCoordinateSystemToWorld()
#ellipsoidTextActor.GetPositionCoordinate().SetValue(8, -14.5, 0)
ellipsoidTextActor.GetPositionCoordinate().SetValue(0, 0, 0)


ren = vtk.vtkRenderer()
renWin = vtk.vtkRenderWindow()
renWin.AddRenderer(ren)

iren = vtk.vtkRenderWindowInteractor()
iren.SetRenderWindow(renWin)

# Add the actors
#ren.AddActor(superEllipsoidActor)
#ren.AddActor(superEllipsoidTextActor)
ren.AddActor(ellipsoidActor)
ren.AddActor(ellipsoidTextActor)

renWin.SetSize(500, 500)

iren.Initialize()
renWin.Render()
iren.Start()