'''
Created on Dec 28, 2010

@author: Shareef Dabdoub
'''
#from data.util import StoreAsMatrix4x4
from render.basic import (Color, ImageRenderer, boolInt)
from store import DataStore

import vtk


class IBCRenderer(ImageRenderer):

    def __init__(self, renderer, renwin_update_callback):
        ImageRenderer.__init__(self)
        self.renderer = renderer
        self.renwin_update_callback = renwin_update_callback
        self.color = None
        self.volumeReader = None
        self.dataSpacing = (0.1, 0.1, 0.56)
        self.isocontourLevel = [20000,20000]
        self.visible = True
        
    @property
    def Settings(self):
        s = {}
        s['ImageSetID'] = self.imageSetID
        s['DataSpacing'] = self.dataSpacing
        s['Color'] = self.color
        s['SliceRange'] = self.volumeReader.sliceRange
        s['PixelExtents'] = self.volumeReader.pixelExtents
        s['IsocontourLevel'] = self.isocontourLevel
        s['Visible'] = self.visible
        
        return s
    
    @Settings.setter
    def Settings(self, s):
        self.imageSetID = s['ImageSetID']
        self.color = s['Color']
        
        if 'DataSpacing' in s:
            self.dataSpacing = s['DataSpacing']
        
        if not isinstance(s['IsocontourLevel'], (list, tuple)):
            self.isocontourLevel = [s['IsocontourLevel'], s['IsocontourLevel']]
        else:
            self.isocontourLevel = s['IsocontourLevel']
        
        if self.volumeReader is not None:
            self.volumeReader.sliceRange = s['SliceRange']
            self.volumeReader.pixelExtents = s['PixelExtents']
            
        if 'Visible' in s:
            self.visible = s['Visible']
        

    def Render(self, volumeReader):
        """
        This method attempts to tesselate the image data.
        
        :@type volumeReader: data.imageIO.base.VolumeImageReader
        :@param volumeReader: This object handles opening image data and 
                              passing it to the appropriate VTK image container
        :@rtype: 2-tuple
        :@return: The vtkActor created from tesselated image data and a 
                  vtkLocator for improving picking operations.
        """
        if self.imageSetID is None: return        
        
        self.volumeReader = volumeReader
        self.vtkReader = volumeReader.LoadVTKReader(self.dataSpacing)
        
        # Gaussian Smoothing
        self.gaussFilter = vtk.vtkImageGaussianSmooth()
        self.gaussFilter.SetDimensionality(3)
        self.gaussFilter.SetStandardDeviation(1)
        self.gaussFilter.SetRadiusFactors(1, 1, 1)
        self.gaussFilter.SetInput(self.vtkReader.GetOutput())
        
        # VOI Extractor
        self.voi = vtk.vtkExtractVOI()
        self.voi.SetInputConnection(self.gaussFilter.GetOutputPort())
#        self.voi.SetInputConnection(self.vtkReader.GetOutputPort())
        self.voi.SetVOI(self.volumeReader.VolumeExtents)
        
        # Surface rendering
        self.bactExtractor = vtk.vtkMarchingCubes()
        self.bactExtractor.GenerateValues(1, self.isocontourLevel)
        self.bactExtractor.ComputeNormalsOff()
        self.bactExtractor.SetInputConnection(self.voi.GetOutputPort())

        # surface rendering with dividing cubes
#        self.bactExtractor = vtk.vtkRecursiveDividingCubes()
#        self.bactExtractor.SetInputConnection(self.voi.GetOutputPort())
#        self.bactExtractor.SetValue(self.isocontourLevel[0])
#        self.bactExtractor.SetDistance(0.5)
#        self.bactExtractor.SetIncrement(2)

        # Smooth the mesh
        relaxedMesh = vtk.vtkSmoothPolyDataFilter()
        relaxedMesh.SetNumberOfIterations(50)
        relaxedMesh.SetInput(self.bactExtractor.GetOutput())

        # Calculate normals
        meshNormals = vtk.vtkPolyDataNormals()
        meshNormals.SetFeatureAngle(60.0)
        meshNormals.SetInput(relaxedMesh.GetOutput())

        # Restrip mesh after normal computation
        restrippedMesh = vtk.vtkStripper()
        restrippedMesh.SetInput(meshNormals.GetOutput())
        
        # Convert mesh to graphics primitives
        self.meshMapper = vtk.vtkPolyDataMapper()
        self.meshMapper.ScalarVisibilityOff()
        self.meshMapper.SetInput(restrippedMesh.GetOutput())
        
        # Finally create a renderable object "Actor" 
        # that can be passed to the render window
        self.ibcActor = vtk.vtkActor()
        self.ibcActor.SetMapper(self.meshMapper)
        ibcColor = DataStore.GetImageSet(self.imageSetID).color
        self.ibcActor.GetProperty().SetDiffuseColor(ibcColor.r, ibcColor.g, ibcColor.b)
        self.ibcActor.GetProperty().SetSpecular(.1)
        self.ibcActor.GetProperty().SetSpecularPower(5)
        self.ibcActor.GetProperty().SetOpacity(1)
        self.ibcActor.SetVisibility(boolInt(self.visible))
        
        self.renderer.AddActor(self.ibcActor)
        
        # Optional Locator to help the ray traced picker
        self.bactLocator = vtk.vtkCellLocator()
        self.bactLocator.SetDataSet(restrippedMesh.GetOutput())
        self.bactLocator.LazyEvaluationOn()
        
        return self.bactLocator
    
    @property
    def VolumeMapper(self):
        return self.meshMapper
    
    @property
    def DescriptiveName(self):
        """
        Get a descriptive name for the files behind the image stack
        """
        return self.vtkReader.GetDescriptiveName()
    
    
    def UpdateDataSpacing(self, dataSpacing):
        self.dataSpacing = dataSpacing
        self.vtkReader.SetDataSpacing(dataSpacing)
        self.vtkReader.Update()
        self.renwin_update_callback()
    
    def UpdateImageDataExtent(self, sliceRange=None, pixelExtents=None):
        """
        :@type sliceRange: list len=2
        :@param sliceRange: Specifies a begin and end slice for the method to 
                            use as extents. i.e. of the given images, only 
                            those in the range will be used as input data 
                            for tesselation.
        :@type pixelExtents: list len=4
        :@param param: 
        """
        if sliceRange is not None:
            self.SliceRange = sliceRange
        if pixelExtents is not None:
            self.volumeReader.pixelExtents = pixelExtents
        
        self.voi.SetVOI(self.volumeReader.VolumeExtents)
        self.voi.Update()
        self.renderer.Render()
    
    def UpdateGaussianFilter(self, stdDev=1, radius=(1,1,1)):
        self.gaussFilter.SetStandardDeviations(stdDev)
        self.gaussFilter.SetRadiusFactors(radius[0], radius[1], radius[2])
        self.gaussFilter.Update()
        self.renwin_update_callback()
    
    
    @property
    def IsocontourLevel(self):
        return self.isocontourLevel
    
    def UpdateIsocontour(self, level):
        if isinstance(level, int):
            level = [level, level]
        
        self.isocontourLevel = level
        self.bactExtractor.GenerateValues(1, self.isocontourLevel)
#        self.bactExtractor.SetValue(self.isocontourLevel[0])
        self.bactExtractor.Update()
        self.renwin_update_callback()
        
    def UpdateColor(self, color):
        self.ibcActor.GetProperty().SetDiffuseColor(color.r, color.g, color.b)
        self.ibcActor.ApplyProperties()
        self.renwin_update_callback()
        
    
    def UpdateVisibility(self, visible):
        self.ibcActor.SetVisibility(boolInt(visible))
        self.renwin_update_callback()
        
    
    # Properties
    @property
    def Actor(self):
        """
        The vtkActor created by this class
        """
        return self.ibcActor

    @property
    def Locator(self):
        """
        The vtkCellLocator created by this class
        """
        return self.bactLocator
        
    @property
    def SliceRange(self):
        """
        Specifies a begin and end slice for the method to 
        use as extents. i.e. of the given images, only 
        those in the range will be used as input data 
        for tesselation.
        """
        return self.volumeReader.sliceRange
    
    @SliceRange.setter
    def SliceRange(self, sliceRange):
        imgSetLen = self.volumeReader.imageArray.GetNumberOfValues()-1
        # error checking on slice range
        if not sliceRange:
            self.volumeReader.sliceRange = [0, imgSetLen]
        else:
            extents = (0, imgSetLen)
            self.volumeReader.sliceRange = (extents[0] if sliceRange[0] < extents[0] else sliceRange[0],
                                            extents[1] if sliceRange[1] > extents[1] else sliceRange[1])
            
            if sliceRange[0] > sliceRange[1]:
                self.volumeReader.sliceRange = [sliceRange[1], sliceRange[0]]
    
#    @property
#    def TransformMatrix(self):
#        return self.ibcActor.GetMatrix()
#    
#    @TransformMatrix.setter
#    def TransformMatrix(self, matrix):
#        self.ibcActor.SetUserMatrix(StoreAsMatrix4x4(matrix))
    

import os.path as osp
import wx

class IBCSettingsDialog(wx.Dialog):
    def __init__(self, parent, ibcRenderer, status_callback=None, title='Image Layer Settings', **kwargs):
        wx.Dialog.__init__(self, parent, size=(360,320), title=title, **kwargs)

        self.ibcRenderer = ibcRenderer
        self.setStatusMessage = status_callback
        
        # Dialog control setup
        sizer = wx.FlexGridSizer(cols=3, vgap=10, hgap=5)
        # image set info
        sizer.Add(wx.StaticText(self, wx.ID_ANY, "Loaded slices:"))
        self.lblImageSetSlices = wx.StaticText(self, wx.ID_ANY, "")
        sizer.Add(self.lblImageSetSlices)
        sizer.AddSpacer(5)
        
        # data spacing
        spacingSizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(wx.StaticText(self, wx.ID_ANY, "Data Spacing:"))
        self.txtSpacingX = wx.TextCtrl(self, wx.ID_ANY, "", size=wx.Size(35, 20))
        self.txtSpacingY = wx.TextCtrl(self, wx.ID_ANY, "", size=wx.Size(35, 20))
        self.txtSpacingZ = wx.TextCtrl(self, wx.ID_ANY, "", size=wx.Size(35, 20))
        spacingSizer.Add(self.txtSpacingX, 0, wx.LEFT, 2)
        spacingSizer.Add(self.txtSpacingY, 0, wx.LEFT, 2)
        spacingSizer.Add(self.txtSpacingZ, 0, wx.LEFT, 2)
        sizer.Add(spacingSizer, 0, wx.RIGHT, 5)
        sizer.AddSpacer(5)
        
        # slice range
        sizer.Add(wx.StaticText(self, wx.ID_ANY, "Slice Range:"))
        self.txtSliceLower = wx.TextCtrl(self, wx.ID_ANY, "")
        self.txtSliceUpper = wx.TextCtrl(self, wx.ID_ANY, "")
        sizer.Add(self.txtSliceLower, 0, wx.RIGHT, 5)
        sizer.Add(self.txtSliceUpper)
        
        # isocontour value
        sizer.Add(wx.StaticText(self, wx.ID_ANY, "Isocontour Value:"))
        self.txtIsocontour = wx.TextCtrl(self, wx.ID_ANY, "")
        sizer.Add(self.txtIsocontour)
        sizer.AddSpacer(5)
        
        # pixel extents
        # X
        sizer.Add(wx.StaticText(self, wx.ID_ANY, "Pixel Extents (X):"))
        self.txtXPixelExtLower = wx.TextCtrl(self, wx.ID_ANY, "")
        self.txtXPixelExtUpper = wx.TextCtrl(self, wx.ID_ANY, "")
        sizer.Add(self.txtXPixelExtLower)
        sizer.Add(self.txtXPixelExtUpper)
        # Y
        sizer.Add(wx.StaticText(self, wx.ID_ANY, "Pixel Extents (Y):"))
        self.txtYPixelExtLower = wx.TextCtrl(self, wx.ID_ANY, "")
        self.txtYPixelExtUpper = wx.TextCtrl(self, wx.ID_ANY, "")
        sizer.Add(self.txtYPixelExtLower)
        sizer.Add(self.txtYPixelExtUpper)
        
        # color picker
        sizer.Add(wx.StaticText(self, wx.ID_ANY, "Color:"))
        self.btnColor = wx.ColourPickerCtrl(self)
        sizer.Add(self.btnColor)
        sizer.AddSpacer(5)
        
        # layer visibility
        sizer.Add(wx.StaticText(self, wx.ID_ANY, "Visible:"))
        self.chkVisible = wx.CheckBox(self, wx.ID_ANY, "")
        sizer.Add(self.chkVisible)
        
        # update button
        self.cmdUpdate = wx.Button(self, wx.NewId(), "Update")
        self.Bind(wx.EVT_BUTTON, self._cmdUpdate_click, id=self.cmdUpdate.Id)
        
        lblInfoSizer = wx.BoxSizer(wx.HORIZONTAL)
        lblInfoSizer.Add(wx.StaticText(self, wx.ID_ANY, "Loaded image set: "))
        self.lblImageSet = wx.StaticText(self, wx.ID_ANY, "None")
        lblInfoSizer.Add(self.lblImageSet)
        
        self.Sizer = wx.BoxSizer(wx.VERTICAL)
        self.Sizer.Add(lblInfoSizer, 0, wx.TOP | wx.LEFT | wx.RIGHT, 10)
        self.Sizer.Add(sizer, 1, wx.EXPAND | wx.LEFT | wx.TOP | wx.BOTTOM | wx.RIGHT, 10)
        self.Sizer.Add(self.cmdUpdate, 0, wx.ALIGN_RIGHT | wx.RIGHT | wx.BOTTOM, 10)
        
        self.settings = self._RetrieveSettings()

        
    #TODO: value sanity checking
    def _cmdUpdate_click(self, events):
        s = self.settings
        
        # data spacing
        if self.txtSpacingX.Value != str(s['DataSpacing'][0]) or \
           self.txtSpacingY.Value != str(s['DataSpacing'][1]) or \
           self.txtSpacingZ.Value != str(s['DataSpacing'][2]):
            print "Updating data spacing"
            self._UpdateDataSpacing()
        
        # image slices
        if self.txtSliceLower.Value != str(s['SliceRange'][0]) or \
           self.txtSliceUpper.Value != str(s['SliceRange'][1]):
            print 'Updating slice range'
            self._UpdateSliceRange()
        
        # isovalues can be a range, so check for '-' and make it a list
        isovals = [int(x) for x in self.txtIsocontour.Value.split('-')]
        if len(isovals) == 1:
            isovals.append(isovals[0])
        if isovals != s['IsocontourLevel']:
            print 'Updating isocontour level'
            self._UpdateIsocontourLevel(isovals)
        
        # pixel extents
        if self.txtXPixelExtLower.Value != str(s['PixelExtents'][0]) or \
           self.txtXPixelExtUpper.Value != str(s['PixelExtents'][1]) or \
           self.txtYPixelExtLower.Value != str(s['PixelExtents'][2]) or \
           self.txtYPixelExtUpper.Value != str(s['PixelExtents'][3]):
            print 'Updating pixel extents'
            self._UpdatePixelExtents()
        
        color = Color.fromWX(self.btnColor.GetColour().Get())
        if color != s['Color']:
            s['Color'] = color
            self._UpdateColor(color)

        # visibility
        visible = self.chkVisible.Value
        if visible != s['Visible']:
            s['Visible'] = visible
            self.ibcRenderer.UpdateVisibility(visible)
            
    
    def _UpdateDataSpacing(self):
        x = float(self.txtSpacingX.Value)
        y = float(self.txtSpacingY.Value)
        z = float(self.txtSpacingZ.Value)
        self.settings['DataSpacing'] = (x, y, z)
        self.ibcRenderer.UpdateDataSpacing((x, y, z))
    
    def _UpdateSliceRange(self):
        lower = int(self.txtSliceLower.Value)
        upper = int(self.txtSliceUpper.Value)
        self.settings['SliceRange'] = (lower, upper)
        self.ibcRenderer.UpdateImageDataExtent((lower, upper))
    
    def _UpdateIsocontourLevel(self, isovals):
        self.settings['IsocontourLevel'] = isovals
        self.ibcRenderer.UpdateIsocontour(isovals)
        
    def _UpdatePixelExtents(self):
        pe = (int(self.txtXPixelExtLower.Value), int(self.txtXPixelExtUpper.Value), 
              int(self.txtYPixelExtLower.Value), int(self.txtYPixelExtUpper.Value))
        self.settings['PixelExtents'] = pe
        self.ibcRenderer.UpdateImageDataExtent(pixelExtents=pe)
        
    def _UpdateColor(self, color):
        self.ibcRenderer.UpdateColor(color)

    def _RetrieveSettings(self):
        """
        Fill the display controls with stored settings.
        """
        s = self.ibcRenderer.Settings
        paths = DataStore.GetImageSet(self.ibcRenderer.ImageSetID).filepaths
        self.lblImageSet.Label = osp.split(osp.commonprefix(paths))[1] + '*'
        self.txtSpacingX.Value = str(s['DataSpacing'][0])
        self.txtSpacingY.Value = str(s['DataSpacing'][1])
        self.txtSpacingZ.Value = str(s['DataSpacing'][2])
        self.lblImageSetSlices.Label = str(s['SliceRange'][1] - s['SliceRange'][0])
        self.txtSliceLower.Value = str(s['SliceRange'][0])
        self.txtSliceUpper.Value = str(s['SliceRange'][1])
        self.txtXPixelExtLower.Value = str(s['PixelExtents'][0])
        self.txtXPixelExtUpper.Value = str(s['PixelExtents'][1])
        self.txtYPixelExtLower.Value = str(s['PixelExtents'][2])
        self.txtYPixelExtUpper.Value = str(s['PixelExtents'][3])
        self.btnColor.SetColour(s['Color'].toWX())
        self.chkVisible.Value = s['Visible']

        # marching cubes can take a range of isocontour values
        if s['IsocontourLevel'][0] == s['IsocontourLevel'][1]:
            self.txtIsocontour.Value = str(s['IsocontourLevel'][0])
        else:
            self.txtIsocontour.Value = str(s['IsocontourLevel'][0]) + '-' + str(s['IsocontourLevel'][1])
        
        return s
















        