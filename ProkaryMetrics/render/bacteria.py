'''
Created on Apr 17, 2011

@author: Shareef Dabdoub

This module contains a set of classes for rendering and storing settings
related to user-created bacteria.
'''
from data.objects import Bacterium
#from data.util import CopyMatrix4x4, StoreAsMatrix4x4
from render.basic import (Color, RenderLayer, BacteriaColor, boolInt, generateSpline)
from store import DataStore
from vector import Vec3f

import vtk
import wx

class BacteriaLayer(RenderLayer):
    def __init__(self, renderer, renwin_update_callback, color=BacteriaColor):
        """
        :@type renderer: vtk.vtkRenderer
        :@param renderer: The 'canvas' into which the bacteria should 
                          be drawn.
        """
        self.renderer = renderer
        self.renwin_update_callback = renwin_update_callback
        self.color = color
        self.markerColor = MarkerColor
        self.actor_radius = 0.5
        self.visible = True

        
    @property
    def Settings(self):
        s = {}
        s['ActorRadius'] = self.actor_radius
        s['Color'] = self.color
        s['Visible'] = self.visible
        return s
    
    @Settings.setter
    def Settings(self, s):
        self.actor_radius = s['ActorRadius']
        self.color = s['Color']
        
        if 'Visible' in s:
            self.visible = s['Visible']
        
    def UpdateRadius(self, radius):
        """
        Set the radius of all actors.
        
        :@type radius: float
        :@param radius: The new radius to use.
        """
        self.actor_radius = radius
        newMarkers = []
        for marker in DataStore.Markers():
            new = Vec3f(marker.GetCenter())
            self.renderer.RemoveActor(marker)
            newMarkers.append(self.CreateMarker(new))
        
        map(self.renderer.AddActor, newMarkers)
        DataStore.ClearMarkers()
        map(DataStore.AddMarker, newMarkers)
        
        for bactActor in DataStore.BacteriaActors():
            self.renderer.RemoveActor(bactActor)
            
        self.AddStoredBacteria()
            
        
        self.renwin_update_callback()
        
    
    def UpdateColor(self, color):
        """
        Set the color of all actors.
        
        :@type color: render.basic.Color
        :@param color: The new color to use.
        """
        self.color = color
        for marker in DataStore.Markers():
            marker.GetProperty().SetDiffuseColor(color.r, 
                                                 color.g, 
                                                 color.b)
        
        for bact in DataStore.BacteriaActors():
            aColl = vtk.vtkPropCollection()
            bact.GetActors(aColl)
            aColl.InitTraversal()
            actors = [aColl.GetNextProp() for _ in range(aColl.GetNumberOfItems())]
            
            for actor in actors:
                actor.GetProperty().SetDiffuseColor(color.r, 
                                                    color.g, 
                                                    color.b)
        self.renwin_update_callback()
        
    
    def UpdateVisibility(self, visible):
        actors = []
        actors.extend(DataStore.Markers())
        actors.extend(DataStore.BacteriaActors())
        for actor in actors:
            actor.SetVisibility(boolInt(visible))
        
        self.renwin_update_callback()
        

    def CreateMarker(self, loc, radius=None):
        """
        :@type loc: Vec3f
        :@param loc: The 3D location of the marker.
        """
        if radius is None:
            radius = self.actor_radius
        sphere = vtk.vtkSphereSource()
        sphere.SetCenter(loc.x, loc.y, loc.z)
        sphere.SetRadius(radius)
        sphere.SetPhiResolution(20)
        sphere.SetThetaResolution(20)
        sphereMapper = vtk.vtkPolyDataMapper()
        sphereMapper.SetInput(sphere.GetOutput())
        sphereActor = vtk.vtkActor()
        sphereActor.SetMapper(sphereMapper)
        sphereActor.GetProperty().SetDiffuseColor(self.markerColor.r, 
                                                  self.markerColor.g, 
                                                  self.markerColor.b)
        sphereActor.SetVisibility(boolInt(self.visible))
        
        return sphereActor
    
    def AddBacterium(self):
        """
        Retrieve the placed markers and replace them with a single actor
        representing a bacterium.
        
        :@rtype: vtk.vtkActor
        :@return: The representation of a bacterium as determined by the number 
                  and placement of markers. 
        """
        markers = DataStore.Markers()
        
        bacterium = self._createBacterium(markers)
    
        DataStore.AddBacterium(Bacterium([marker.GetCenter() for marker in markers]))
        DataStore.AddBacteriumActor(bacterium)
        self.renderer.AddActor(bacterium)
            
        # Cleanup
        for marker in DataStore.Markers():
            self.renderer.RemoveActor(marker)
        DataStore.ClearMarkers()
        
    
    def AddStoredBacteria(self):
        """
        Create VTK Actors for each Bacterium object in the DataStore
        """
        for bacterium in DataStore.Bacteria():
            markers = [self.CreateMarker(loc) for loc in bacterium.Markers]
            
            bacterium = self._createBacterium(markers)
        
            DataStore.AddBacteriumActor(bacterium)
            self.renderer.AddActor(bacterium)
            
#    def CaptureTransforms(self):
#        """
#        Copy the transform matrices for all user-placed actors.
#        """
#        markersM = []
#        bactsM = []
#        
#        for marker in DataStore.Markers():
#            markersM.append(CopyMatrix4x4(marker.GetMatrix))
#            
#        for bact in DataStore.BacteriaActors():
#            bactsM.append(CopyMatrix4x4(bact.GetMatrix))
#            
#        return markersM, bactsM
#    
#    def ApplyTransforms(self, markersM, bactsM):
#        """
#        Apply previously captured transform matrices.
#        """
#        for i, marker in DataStore.Markers():
#            marker.SetUserMatrix(StoreAsMatrix4x4(markersM[i]))
#        
#        for i, bact in DataStore.BacteriaActors():
#            bact.SetUserMatrix(StoreAsMatrix4x4(bactsM[i]))
    
    
    def _createBacterium(self, markers):
        
        if len(markers) == 1:
            return self._createCoccoid(markers) 
        
        if len(markers) == 2:
            return self._createBacillus(markers)
        
        if len(markers) > 2:
            return self._createFilamentSpline(markers)
    
        
    def _createCoccoid(self, markers):
        """
        A coccoid-form bacterium is basically spherical, so this method
        returns the input marker, possibly changing the radius 
        and/or color.
        
        :@type markers: list
        :@param markers: A list containing a single vtkActor marking the presence
                         of a coccoid bacterium.
        :@rtype: vtkActor
        :@return: A sphere vtkActor representing the marked coccoid bacterium.
        """
        markers[0].GetProperty().SetDiffuseColor(self.color.r, self.color.g, self.color.b)
        return markers[0]
    
    
    def _createBacillus(self, markers):
        """
        A bacillus-form bacterium is marked by two markers, so this 
        method replaces those markers with a sphere-cylinder-sphere 
        vtkAssembly that well-approximates the bacillus shape. 
        The spheres are identical to the input markers and the 
        cylinder's endpoints are at their respective centers. 
        """
        c1 = Vec3f(markers[0].GetCenter())
        c2 = Vec3f(markers[1].GetCenter()) 

        cylActor = self._createCylinder(c1, c2)
    
        markers[0].GetProperty().SetDiffuseColor(self.color.r, self.color.g, self.color.b)
        cylActor.GetProperty().SetDiffuseColor(self.color.r, self.color.g, self.color.b)
        markers[1].GetProperty().SetDiffuseColor(self.color.r, self.color.g, self.color.b)
        
        # join separate pieces into a vtkAssembly
        bacillus = vtk.vtkAssembly()
        bacillus.AddPart(markers[0])
        bacillus.AddPart(cylActor)
        bacillus.AddPart(markers[1])
        
        return bacillus
    
    
    def _createFilament(self, markers):
        filament = vtk.vtkAssembly()
        filament.AddPart(markers[0])
        
        for i, marker in enumerate(markers[1:]):
            prevMarker = markers[i]
            cylActor = self._createCylinder(Vec3f(prevMarker.GetCenter()), Vec3f(marker.GetCenter()))
            filament.AddPart(cylActor)
            filament.AddPart(marker)
    
        return filament
    
    def _createFilamentSpline(self, markers):
        profileData = vtk.vtkPolyData()
        points, scalars, t, sList = generateSpline(markers)
        fradius = self.actor_radius * 1.5
        
        # Create the polyline.
        lines = vtk.vtkCellArray()
        lines.InsertNextCell(len(sList))
        for i in range(len(sList)):
            lines.InsertCellPoint(i)
         
        profileData.SetPoints(points)
        profileData.SetLines(lines)
        profileData.GetPointData().SetScalars(scalars)
        
        # Add thickness to the resulting line.
        profileTubes = vtk.vtkTubeFilter()
        profileTubes.SetNumberOfSides(20)
        profileTubes.SetInput(profileData)
        profileTubes.SetRadius(fradius)
            
        profileMapper = vtk.vtkPolyDataMapper()
        profileMapper.SetInput(profileTubes.GetOutput())
        profileMapper.SetScalarRange(0,t)
        profileMapper.ScalarVisibilityOff()
        
        profile = vtk.vtkActor()
        profile.SetMapper(profileMapper)
        profile.GetProperty().SetDiffuseColor(self.color.r, self.color.g, self.color.b)
    #    profile.GetProperty().SetSpecular(.3)
    #    profile.GetProperty().SetSpecularPower(30)
    
        markers[0].GetProperty().SetDiffuseColor(self.color.r, self.color.g, self.color.b)
        markers[-1].GetProperty().SetDiffuseColor(self.color.r, self.color.g, self.color.b)
    
        # Add capping spheres
        filament = vtk.vtkAssembly()
        filament.AddPart(self.CreateMarker(Vec3f(markers[0].GetCenter()), fradius))
        filament.AddPart(profile)
        filament.AddPart(self.CreateMarker(Vec3f(markers[-1].GetCenter()), fradius))
        
        return filament
    
    def _createCylinder(self, endPt1, endPt2, res=20):
        """
        Create a cylinder oriented to have the given end points.
        
        :@type endPt1: Vec3f
        :@param endPt1: The first end point to align the cylinder with.
        :@type endPt2: Vec3f
        :@param endPt2: The second end point to align the cylinder with.
        :@type radius: float
        :@param radius: The radius of the cylinder.
        :@type res: int
        :@param res: The circular resolution of the cylinder (number of sides). 
                     Must be at least 3.
                     
        :@rtype: vtk.vtkActor
        :@return: A renderable actor representing a cylinder.
        """
        res = 3 if res < 3 else res
        line = vtk.vtkLineSource()
        line.SetPoint1(endPt1.x,endPt1.y,endPt1.z)
        line.SetPoint2(endPt2.x,endPt2.y,endPt2.z)
        # Create a tube filter to represent the line as a cylinder.
        tube = vtk.vtkTubeFilter()
        tube.SetInput(line.GetOutput())
        tube.SetRadius(self.actor_radius)
        tube.SetNumberOfSides(res)
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(tube.GetOutputPort())
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        
        return actor    

class BacteriaLayerSettingsDialog(wx.Dialog):
    def __init__(self, parent, bactLayer, status_callback=None, title='Bacteria Layer Settings', **kwargs):
        wx.Dialog.__init__(self, parent, size=(180,160), title=title, **kwargs)

        self.bactLayer = bactLayer
        self.setStatusMessage = status_callback
        
        # Dialog control setup
        sizer = wx.FlexGridSizer(cols=2, vgap=5, hgap=10)
        
        # actor radius
        sizer.Add(wx.StaticText(self, wx.ID_ANY, "Radius:"))
        self.txtRadius = wx.TextCtrl(self, wx.ID_ANY, "")
        sizer.Add(self.txtRadius)
        
        # color picker
        sizer.Add(wx.StaticText(self, wx.ID_ANY, "Color:"))
        self.btnColor = wx.ColourPickerCtrl(self)
        sizer.Add(self.btnColor)
        
        # layer visibility
        sizer.Add(wx.StaticText(self, wx.ID_ANY, "Visible:"))
        self.chkVisible = wx.CheckBox(self, wx.ID_ANY, "")
        sizer.Add(self.chkVisible)
        
        # update button
        self.cmdUpdate = wx.Button(self, wx.NewId(), "Update")
        self.Bind(wx.EVT_BUTTON, self._cmdUpdate_click, id=self.cmdUpdate.Id)
        
        self.Sizer = wx.BoxSizer(wx.VERTICAL)
        self.Sizer.Add(sizer, 1, wx.EXPAND | wx.LEFT | wx.ALL, 15)
        self.Sizer.Add(self.cmdUpdate, 0, wx.ALIGN_RIGHT | wx.RIGHT | wx.LEFT | wx.BOTTOM, 10)
        
        self.settings = self._RetrieveSettings()

        
    #TODO: value sanity checking
    def _cmdUpdate_click(self, events):
        s = self.settings
        
        radius = float(self.txtRadius.Value)
        if radius != s['ActorRadius']:
            self.bactLayer.UpdateRadius(radius)
            s['ActorRadius'] = radius
        
        visible = self.chkVisible.Value
        if visible != s['Visible']:
            self.bactLayer.UpdateVisibility(visible)
            s['Visible'] = visible
        
        color = Color.fromWX(self.btnColor.GetColour().Get())
        if color != s['Color']:
            self.bactLayer.UpdateColor(color)
            s['Color'] = color
        
        
        
    def _RetrieveSettings(self):    
        """
        Fill the display controls with stored settings.
        """
        s = self.bactLayer.Settings
        
        self.txtRadius.Value = str(s['ActorRadius'])
        self.btnColor.SetColour(s['Color'].toWX())
        self.chkVisible.Value = s['Visible']
        
        return s
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        