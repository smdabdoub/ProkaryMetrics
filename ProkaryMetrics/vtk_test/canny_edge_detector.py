'''
Created on Jan 20, 2011

@author: shareef
'''
import vtk

# Define viewport ranges
# (xmin, ymin, xmax, ymax)

originalViewport = [0.0, 0.0, 0.5, 1.0]
edgeViewport = [0.5, 0.0, 1.0, 1.0]

originalRenderer = vtk.vtkRenderer()
originalRenderer.SetViewport(originalViewport)
edgeRenderer = vtk.vtkRenderer()
edgeRenderer.SetViewport(edgeViewport)

renderWindow = vtk.vtkRenderWindow()
renderWindow.SetSize(600,300)
renderWindow.SetMultiSamples(0)
renderWindow.AddRenderer(originalRenderer)
renderWindow.AddRenderer(edgeRenderer)

interactor = vtk.vtkRenderWindowInteractor()
interactor.SetRenderWindow(renderWindow)

imageIn = vtk.vtkPNGReader()
imageIn.SetFileName("bact_test_small.png")
imageIn.Update()

imageActor = vtk.vtkImageActor()
imageActor.SetInput(imageIn.GetOutput())
originalRenderer.AddActor(imageActor)

il = vtk.vtkImageLuminance()
il.SetInputConnection(imageIn.GetOutputPort())

ic = vtk.vtkImageCast()
ic.SetOutputScalarTypeToFloat()
ic.SetInputConnection(il.GetOutputPort())

# Smooth the image
gs = vtk.vtkImageGaussianSmooth()
gs.SetInputConnection(ic.GetOutputPort())
gs.SetDimensionality(2)
gs.SetRadiusFactors(1, 1, 0)

# Gradient the image
imgGradient = vtk.vtkImageGradient()
imgGradient.SetInputConnection(gs.GetOutputPort())
imgGradient.SetDimensionality(2)

imgMagnitude = vtk.vtkImageMagnitude()
imgMagnitude.SetInputConnection(imgGradient.GetOutputPort())

# Non maximum suppression
nonMax = vtk.vtkImageNonMaximumSuppression()
nonMax.SetMagnitudeInput(imgMagnitude.GetOutput())
nonMax.SetVectorInput(imgGradient.GetOutput())
nonMax.SetDimensionality(2)

pad = vtk.vtkImageConstantPad()
pad.SetInputConnection(imgGradient.GetOutputPort())
pad.SetOutputNumberOfScalarComponents(3)
pad.SetConstant(0)

i2sp1 = vtk.vtkImageToStructuredPoints()
i2sp1.SetInputConnection(nonMax.GetOutputPort())
i2sp1.SetVectorInput(pad.GetOutput())

# Link edgles
imgLink = vtk.vtkLinkEdgels()
imgLink.SetInputConnection(i2sp1.GetOutputPort())
imgLink.SetGradientThreshold(2)

# Threshold links
thresholdEdgels = vtk.vtkThreshold()
thresholdEdgels.SetInputConnection(imgLink.GetOutputPort())
thresholdEdgels.ThresholdByUpper(10)
thresholdEdgels.AllScalarsOff()

gf = vtk.vtkGeometryFilter()
gf.SetInputConnection(thresholdEdgels.GetOutputPort())

i2sp = vtk.vtkImageToStructuredPoints()
i2sp.SetInputConnection(imgMagnitude.GetOutputPort())
i2sp.SetVectorInput(pad.GetOutput())

# Subpixel them
spe = vtk.vtkSubPixelPositionEdgels()
spe.SetInputConnection(gf.GetOutputPort())
spe.SetGradMaps(i2sp.GetStructuredPointsOutput())

strip = vtk.vtkStripper()
strip.SetInputConnection(spe.GetOutputPort())

dsm = vtk.vtkPolyDataMapper()
dsm.SetInputConnection(strip.GetOutputPort())
dsm.ScalarVisibilityOff()

planeActor = vtk.vtkActor()
planeActor.SetMapper(dsm)
planeActor.GetProperty().SetAmbient(1.0)
planeActor.GetProperty().SetDiffuse(0.0)

# Add the actors to the renderer, set the background and size
edgeRenderer.AddActor(planeActor)

# Render the image
interactor.Initialize()
renderWindow.Render()
renderWindow.Render()

interactor.Start()
