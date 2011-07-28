from data.calc import fitEllipsoid
from render.ibc import IBCRenderer
from render.bacteria import BacteriaLayer
from render.basic import boolInt
from store import DataStore
from vector import Vec3f
from wxVTK.wxVTKRenderWindowInteractor import wxVTKRenderWindowInteractor

import math
import vtk
import wx

class IBCRenderPanel(wx.Panel):
    """
    The panel class used for displaying and interacting with 3D microscope data.
    """
    def __init__( self, parent, imode_callback, rmode_callback, ppos_callback, **kwargs ):
        # initialize Panel
        if 'id' not in kwargs:
            kwargs['id'] = wx.ID_ANY
        wx.Panel.__init__( self, parent, **kwargs )

        self.setInteractionMode = imode_callback
        self.setInteractionMode(False)
        
        self.recordingMode = False
        self.setRecordingMode = rmode_callback
        self.setRecordingMode(False)
        
        self.setPickerPos = ppos_callback
        

        self.vtkWidget = wxVTKRenderWindowInteractor(self, wx.ID_ANY)
        self.iren = self.vtkWidget._Iren
        self.iren.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())
        
        self.renderer = vtk.vtkRenderer()
        self.imageLayer = IBCRenderer(self.renderer, self.iren.Render)
        self.bacteriaLayer = BacteriaLayer(self.renderer, self.iren.Render)
        
        # for interactive clipping
        self.planes = vtk.vtkPlanes()
        
        self.ellipsoid = None
        self.ellipsoidTextActor = None
        
        # The SetInteractor method is how 3D widgets are associated with the
        # render window interactor. Internally, SetInteractor sets up a bunch
        # of callbacks using the Command/Observer mechanism (AddObserver()).
        self.boxWidget = vtk.vtkBoxWidget()
        self.boxWidget.SetInteractor(self.iren)
        self.boxWidget.SetPlaceFactor(1.0)

        # init vtk window
        self.vtkWidget.Enable(1)
        self.vtkWidget.AddObserver("ExitEvent", lambda o,e,f=parent: f.Close())
        self.vtkWidget.GetRenderWindow().AddRenderer(self.renderer)
        
        # Bind VTK events
        self.iren.AddObserver("KeyPressEvent", self.OnKeyDown)
        
        self.Sizer = wx.BoxSizer()
        self.Sizer.Add(self.vtkWidget, 1, wx.EXPAND)
        

    def initPicker(self):
        coneSource = vtk.vtkConeSource()
        coneSource.CappingOn()
        coneSource.SetHeight(2)
        coneSource.SetRadius(1)
        coneSource.SetResolution(10)
        coneSource.SetCenter(1,0,0)
        coneSource.SetDirection(-1,0,0)
        
        coneMapper = vtk.vtkDataSetMapper()
        coneMapper.SetInputConnection(coneSource.GetOutputPort())
        
        self.redCone = vtk.vtkActor()
        self.redCone.PickableOff()
        self.redCone.SetMapper(coneMapper)
        self.redCone.GetProperty().SetColor(1,0,0)
        
        self.greenCone = vtk.vtkActor()
        self.greenCone.PickableOff()
        self.greenCone.SetMapper(coneMapper)
        self.greenCone.GetProperty().SetColor(0,1,0)
        
        # Add the two cones (or just one, if you want)
        self.renderer.AddViewProp(self.redCone)
        self.renderer.AddViewProp(self.greenCone)
        
        self.picker = vtk.vtkVolumePicker()
        self.picker.SetTolerance(1e-6)
        self.picker.SetVolumeOpacityIsovalue(0.1)
        
    def _pickerVisibility(self, visible):
        self.redCone.SetVisibility(boolInt(visible))
        self.greenCone.SetVisibility(boolInt(visible))
        
    def initBoxWidgetInteraction(self, imageOutput):
        # set up interaction handling
        self.boxWidget.SetInput(imageOutput)
        self.boxWidget.PlaceWidget()
        self.boxWidget.InsideOutOn()
        self.boxWidget.AddObserver("StartInteractionEvent", self.StartInteraction)
        self.boxWidget.AddObserver("InteractionEvent", self.ClipVolumeRender)
        self.boxWidget.AddObserver("EndInteractionEvent", self.EndInteraction)
        
        # set up box widget representation
        outlineProperty = self.boxWidget.GetOutlineProperty()
        outlineProperty.SetRepresentationToWireframe()
        outlineProperty.SetAmbient(1.0)
        outlineProperty.SetAmbientColor(1, 1, 1)
        outlineProperty.SetLineWidth(3)
        selectedOutlineProperty = self.boxWidget.GetSelectedOutlineProperty()
        selectedOutlineProperty.SetRepresentationToWireframe()
        selectedOutlineProperty.SetAmbient(1.0)
        selectedOutlineProperty.SetAmbientColor(1, 0, 0)
        selectedOutlineProperty.SetLineWidth(3)
    

    def RenderImageData(self, id, imgReader):
        self.imageLayer.SetImageSet(id)
        locator = self.imageLayer.Render(imgReader)
        self.initPicker()
        self.picker.AddLocator(locator)
        self.initBoxWidgetInteraction(imgReader.VolumeReader.GetOutput())
        
        self.iren.AddObserver("MouseMoveEvent", self.MoveCursor)
        self.iren.AddObserver("LeftButtonPressEvent", self.LeftClick)
        self.iren.AddObserver("RightButtonPressEvent", self.RightClick)
        
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
        self.renderer.SetActiveCamera(aCamera)
        self.renderer.ResetCamera() 
        aCamera.Dolly(1.0)
        self.renderer.ResetCameraClippingRange()
        self.iren.Render()

    def RecordBacterium(self):
        """
        Creates an internal representation of a bacterium as well as 
        creating a vtkActor representation and stores both in the DataStore, 
        then refreshes the render window. 
        """
        self.bacteriaLayer.AddBacterium()
        self.iren.Render()
        
    def RenderStoredBacteria(self):
        self.bacteriaLayer.AddStoredBacteria()
        self.renderer.Render()
        
    def DeleteBacterium(self, idx=None):
        """
        Delete the recorded bacterium (internal and actor) 
        at the specified index.
        
        Note: if no index is passed, the most recently added 
              bacterium is deleted.
        
        :@type idx: int
        :@param idx: The index of the bacterium to delete 
        """
        if (not len(DataStore.Bacteria())):
            return
        
        if idx is None:
            idx = -1
        
        # remove actor from renderer
        self.renderer.RemoveActor(DataStore.BacteriaActors()[idx])
        
        del DataStore.Bacteria()[idx]
        del DataStore.BacteriaActors()[idx]
        
        self.iren.Render()

    def RenderFittedEllipsoid(self):
        # if fit already exists, clear b/f fitting again
        if self.ellipsoid:
            self.renderer.RemoveActor(self.ellipsoid)
            self.renderer.RemoveActor(self.ellipsoidTextActor)
            
        self.ellipsoid, self.ellipsoidTextActor = fitEllipsoid(self.bacteriaLayer.actor_radius)
        self.renderer.AddActor(self.ellipsoid)
        self.renderer.AddActor(self.ellipsoidTextActor)
        self.iren.Render()
    
    def ToggleEllipsoidVisibility(self):
        vstate = [1,0]
        if self.ellipsoid:
            self.ellipsoid.SetVisibility(vstate[self.ellipsoid.GetVisibility()])
            self.ellipsoidTextActor.SetVisibility(vstate[self.ellipsoidTextActor.GetVisibility()])


    
    # ACCESSORS/MODIFIERS
    @property
    def ImageLayer(self):
        """
        Returns a reference to the IBCRenderer class that 
        tesselates the data into a vtkActor.
        
        :@rtype: render.ibc.IBCRenderer
        """
        return self.imageLayer
    
    @property
    def BacteriaLayer(self):
        """
        Returns a reference to the BacteriaLayer class that 
        handles storing and representing user-placed markers 
        and bacteria.
        """
        return self.bacteriaLayer
    
    @property
    def BacteriaRenderer(self):
        """
        Returns a reference to the vtkRenderer layer that 
        recorded bacteria are drawn into.
        
        :@rtype: vtk.vtkRenderer
        """
        return self.renderer
#        return self.bactRenderer


    # EVENT HANDLING
    def LeftClick(self, iren, event):
        if self.recordingMode:
            pos = Vec3f(self.picker.GetPickPosition())
            actor = self.bacteriaLayer.CreateMarker(pos)
            self.renderer.AddActor(actor)
            DataStore.AddMarker(actor)
            self.iren.Render()
    
    def RightClick(self, iren, event):
        pos = Vec3f(self.picker.GetPickPosition())
        minDist = -1
        minMarker = None
        mid = None
        
        if not len(DataStore.Markers()):
            return
        
        # find the closest marker to the click position
        for i, marker in enumerate(DataStore.Markers()):
            mpos = Vec3f(marker.GetCenter())
            diff = pos - mpos
            dlen = diff.length()
            if minDist < 0 or dlen < minDist:
                minDist = diff.length()
                minMarker = marker
                mid = i
        
        # make sure the user clicked somewhere near a marker before removing
        if minDist <= self.bacteriaLayer.actor_radius * 2:
            self.renderer.RemoveActor(minMarker)
            del DataStore.Markers()[mid]
            
            self.iren.Render()

    
    def OnKeyDown(self, iren, event):
        key = iren.GetKeyCode().upper()
        if key == 'T':
            self.setInteractionMode()
        elif key == 'J':
            self.setInteractionMode(False)
        elif key == 'X':
            if self.recordingMode:
                self.recordingMode = False
                self.setRecordingMode(self.recordingMode)
            else:
                self.recordingMode = True
                self.setRecordingMode()
        elif key == 'D':
            self.OnDeleteRequest()
        elif key == ',':
            self.MoveEllipsoid()
        elif key == '.':
            self.MoveEllipsoidText()
            
    
    def OnDeleteRequest(self):
        minDist = -1
        bactID = None
        
        if not len(DataStore.Bacteria()):
            return
        
        pos = Vec3f(self.picker.GetPickPosition())
        # find the closest bacterium to the click position
        for i, bact in enumerate(DataStore.Bacteria()):
            for _, marker in enumerate(bact.Markers):
                diff = pos - marker
                dlen = diff.length()
                if minDist < 0 or dlen < minDist:
                    minDist = diff.length()
                    bactID = i
        
        # make sure the user clicked somewhere near a marker before removing
        if minDist <= self.bacteriaLayer.actor_radius * 5:
            self.DeleteBacterium(bactID)
            
    def MoveEllipsoid(self):
        if self.ellipsoid:
            pos = Vec3f(self.picker.GetPickPosition())
            self.ellipsoid.SetPosition(pos.x, pos.y, pos.z)
            self.iren.Render()
    
    def MoveEllipsoidText(self):
        if self.ellipsoidTextActor:
            pos = Vec3f(self.picker.GetPickPosition())
            self.ellipsoidTextActor.SetPosition((pos.x, pos.y))
            self.iren.Render()

 
    def MoveCursor(self, iren, event=""):
#        self.vtkWidget.GetRenderWindow().HideCursor()
        x,y = self.iren.GetEventPosition()
        self.picker.Pick(x, y, 0, self.renderer)
        p = self.picker.GetPickPosition()
        self.setPickerPos(Vec3f(p))
        n = self.picker.GetPickNormal()
        self.redCone.SetPosition(p[0],p[1],p[2])
        self.PointCone(self.redCone,n[0],n[1],n[2])
        self.greenCone.SetPosition(p[0],p[1],p[2])
        self.PointCone(self.greenCone,-n[0],-n[1],-n[2])
        iren.Render()
        
        
    def StartInteraction(self, obj, event):
        """
        Lower the rendering resolution to make interaction more smooth.
        """
        self.vtkWidget.GetRenderWindow().SetDesiredUpdateRate(10)
        self._pickerVisibility(False)
    
    def EndInteraction(self, obj, event):
        """
        When interaction ends, the requested frame rate is decreased to
        normal levels. This causes a full resolution render to occur.
        """
        self.vtkWidget.GetRenderWindow().SetDesiredUpdateRate(0.001)
        self._pickerVisibility(True)
        
    def ClipVolumeRender(self, obj, event):
        obj.GetPlanes(self.planes)
        self.imageLayer.VolumeMapper.SetClippingPlanes(self.planes)
        
    
    # UTILITY METHODS
    def PointCone(self, actor, nx, ny, nz):
        actor.SetOrientation(0.0, 0.0, 0.0)
        n = math.sqrt(nx**2 + ny**2 + nz**2)
        if (nx < 0.0):
            actor.RotateWXYZ(180, 0, 1, 0)
            n = -n
        actor.RotateWXYZ(180, (nx+n)*0.5, ny*0.5, nz*0.5)
        
        
        
        
        
        
        
        