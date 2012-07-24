import data.io as dio
from data.imageIO import export
import data.imageIO.types as imageIOTypes
from render.basic import IBCColor
from render.ibc import IBCSettingsDialog
from render.bacteria import BacteriaLayerSettingsDialog
from settings import RenderActionsPanel
from store import DataStore
from vector import Vec3f
from view.dialogs import SelectImageLayerDialog
from vtkRender import IBCRenderPanel

import wx
import os.path
import sys

# CONSTANTS
ID_OPEN = wx.NewId()
ID_LOAD_PROJECT = wx.NewId()
ID_SAVE_PROJECT = wx.NewId()
ID_EXPORT_BACTERIA = wx.NewId()
ID_EXPORT_LENGTHS = wx.NewId()
ID_EXPORT_ORIENTATIONS = wx.NewId()

ID_DYNGAUSS = wx.NewId()

ID_FIT_MVE_ELLIPSOID = wx.NewId()
ID_FIT_LOWNER_ELLIPSOID = wx.NewId()
ID_TOGGLE_ELLIPSOID_VIS = wx.NewId()

# Color schemes for orientation coloring
ID_RGB = wx.NewId()
ID_GBR = wx.NewId()
ID_BGR = wx.NewId()

ID_VIEW_SELECT_IMAGE_LAYER = wx.NewId()
ID_VIEW_IMAGE_LAYER_SETTINGS = wx.NewId()
ID_VIEW_BACTERIA_LAYER_SETTINGS = wx.NewId()


class MainWindow(wx.Frame):
    """
    Main display window for the project.
    """
    
    def __init__(self,parent,ID,title):
        wx.Frame.__init__(self, parent, wx.ID_ANY, title, size=(800,700))
        self.Center(direction=wx.HORIZONTAL)

        # Set up status bar
        self.StatusBar = self.CreateStatusBar(4)
        self.StatusBar.SetStatusWidths([-3, 150, -1, -1])
        self.StatusBar.SetStatusStyles([wx.SB_NORMAL, wx.SB_NORMAL, wx.SB_RAISED, wx.SB_RAISED])

        self.Sizer = wx.BoxSizer(wx.VERTICAL)
        self.pnlIBCRender = IBCRenderPanel(self, imode_callback=self.setInteractionMode, 
                                                 rmode_callback=self.setRecordingMode, 
                                                 ppos_callback=self.setPickerPosition,
                                                 ao=self.AppendOutput)
        self.pnlActions =  RenderActionsPanel(self, self.pnlIBCRender, 
                                              status_callback=self.setMainStatus)
        self.pnlIBCRender.updateCount = self.pnlActions.UpdateBacteriaCount()
        
        self.txtOutput = wx.TextCtrl(self, style=wx.TE_READONLY|wx.TE_MULTILINE)
        self.txtOutput.Hide()
        
        self.Sizer.Add(self.pnlIBCRender, 1, wx.EXPAND | wx.BOTTOM, 10)
        self.Sizer.Add(self.pnlActions, 0, wx.EXPAND  | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)
        self.Sizer.Add(self.txtOutput, 0, wx.EXPAND|wx.LEFT|wx.RIGHT, 5)
        
        # File menu
        fileMenu = wx.Menu()
        # Open file
        fileMenu.Append(ID_OPEN, "Add Image Stack...\tCtrl+O"," Open a file to edit")
        self.Bind(wx.EVT_MENU, self.OnOpen, id=ID_OPEN)
        # Load project
        fileMenu.Append(ID_LOAD_PROJECT, "Load Project...\tCtrl+L"," Load a saved project")
        self.Bind(wx.EVT_MENU, self.OnLoadProject, id=ID_LOAD_PROJECT)
        # Save project
        fileMenu.Append(ID_SAVE_PROJECT, "Save Project...\tCtrl+S"," Save your work to a file")
        self.Bind(wx.EVT_MENU, self.OnSaveProject, id=ID_SAVE_PROJECT)
        ## Export Submenu
        exportSubMenu = wx.Menu()
        fileMenu.AppendSubMenu(exportSubMenu, "Export", "Tools for exporting quantitative data")
        ### Export Bacteria
        exportSubMenu.Append(ID_EXPORT_BACTERIA, "Bacteria...",
                             "Export a csv listing the recorded markers for all bacteria")
        self.Bind(wx.EVT_MENU, self.OnExport, id=ID_EXPORT_BACTERIA)
        ### Export Lengths
        exportSubMenu.Append(ID_EXPORT_LENGTHS, "Lengths...",
                             "Export a csv of the lengths of recorded bacteria")
        self.Bind(wx.EVT_MENU, self.OnExport, id=ID_EXPORT_LENGTHS)
        ### Export orientations
        exportSubMenu.Append(ID_EXPORT_ORIENTATIONS, "Orientation Data...",
                             "Export a csv of the X/Y/Z orientations of recorded bacteria")
        self.Bind(wx.EVT_MENU, self.OnExport, id=ID_EXPORT_ORIENTATIONS)
        # Exit
        item = fileMenu.Append(wx.ID_EXIT,"E&xit"," Terminate the program")
        self.Bind(wx.EVT_MENU, self.OnMenuExit, item)
        
        # Data menu
#        dataMenu = wx.Menu()
#        dataMenu.Append(ID_DYNGAUSS, "Convert to PPM...", 
#        "Convert loaded image set to PPM files for use with the Dynamic Gaussian algorithm.")
#        self.Bind(wx.EVT_MENU, self.OnDynGauss, id=ID_DYNGAUSS)
        
        # Tools menu
        toolsMenu = wx.Menu()
        fitSubMenu = wx.Menu()
        orientSubMenu = wx.Menu()
        toolsMenu.AppendSubMenu(fitSubMenu, "Volume Estimation", 
                                """Use the recorded bacteria or placed \
                                markers to fit an ellipsoid for estimation \
                                of volume and general shape""")
        toolsMenu.AppendSubMenu(orientSubMenu, "Orientation",
                                """Calculate information and statistics about \ 
                                the orientation of the recorded bacteria \
                                with respect to the 3 axes""")
        # Ellipsoid Fitting options
        fitSubMenu.Append(ID_FIT_MVE_ELLIPSOID, "Fit MVE Ellipsoid", 
                          "Fit an ellipsoid using the Minimum Volume method")
        self.Bind(wx.EVT_MENU, self.OnFitEllipsoid, id=ID_FIT_MVE_ELLIPSOID)
        fitSubMenu.Append(ID_FIT_LOWNER_ELLIPSOID, "Fit Lowner Ellipsoid", 
                          "Fit an ellipsoid using the Lowner method")
        self.Bind(wx.EVT_MENU, self.OnFitEllipsoid, id=ID_FIT_LOWNER_ELLIPSOID)
        
        self.toolsToggleEVis = wx.MenuItem(toolsMenu, ID_TOGGLE_ELLIPSOID_VIS, 
                                      "Toggle Ellipsoid Visibility")
        self.toolsToggleEVis.Enable(False)
        fitSubMenu.AppendItem(self.toolsToggleEVis)
        self.Bind(wx.EVT_MENU, self.OnToggleEllipsoidVis, id=ID_TOGGLE_ELLIPSOID_VIS)
        
        # Orientation calculation options
        #   stats
        itemCalcOrient = wx.MenuItem(toolsMenu, wx.NewId(), "Calculate Orientation Stats",
                                     "Calculate descriptive statistics for bacteria orientation")
        orientSubMenu.AppendItem(itemCalcOrient)
        self.Bind(wx.EVT_MENU, self.OnCalcOrientation, id=itemCalcOrient.GetId())
        #   color by
        colorOrientSubMenu = wx.Menu()
        orientSubMenu.AppendSubMenu(colorOrientSubMenu, "Color Bacteria by Orientation", "")
        colorOrientSubMenu.Append(ID_RGB, "XYZ -> RGB", """Color the bacteria by orientation \
                                  such that the X component is in the Red channel and so on""")
        colorOrientSubMenu.Append(ID_GBR, "XYZ -> GBR", """Color the bacteria by orientation \
                                  such that the X component is in the Green channel and so on""")
        colorOrientSubMenu.Append(ID_BGR, "XYZ -> BGR", """Color the bacteria by orientation \
                                  such that the X component is in the Blue channel and so on""")
        self.Bind(wx.EVT_MENU, self.OnColorByOrientation, id=ID_RGB)
        self.Bind(wx.EVT_MENU, self.OnColorByOrientation, id=ID_GBR)
        self.Bind(wx.EVT_MENU, self.OnColorByOrientation, id=ID_BGR)
        
        # back to the tools menu items
        #   stats
        toolsCalcCommDensity = wx.MenuItem(toolsMenu, wx.NewId(), "Calculate Community Distance Stats",
                                     "Calculate descriptive statistics for the distance between bacteria.")
        toolsMenu.AppendItem(toolsCalcCommDensity)
        self.Bind(wx.EVT_MENU, self.OnCalcCommDensity, id=toolsCalcCommDensity.GetId())
        
        toolsScreenshot = wx.MenuItem(toolsMenu, wx.NewId(), 'Take Screenshot',
                                      """Saves the contents of the display \
                                      window to an image file""")
        toolsMenu.AppendItem(toolsScreenshot)
        self.Bind(wx.EVT_MENU, self.TakeScreenshot, id=toolsScreenshot.GetId())
        
        # View menu
        viewMenu = wx.Menu()
        # Select Image Layer dlg
        viewMenu.Append(ID_VIEW_SELECT_IMAGE_LAYER, "Select Image Layer", 
                        "Change the currently selected image layer")
        self.Bind(wx.EVT_MENU, self.OnSelectImageLayer, 
                  id=ID_VIEW_SELECT_IMAGE_LAYER)
        # Image Layer dlg
        viewMenu.Append(ID_VIEW_IMAGE_LAYER_SETTINGS, "Image Layer Settings", 
                        "Shows a dialog for changing image rendering settings")
        self.Bind(wx.EVT_MENU, self.OnViewImageLayerSettings, 
                  id=ID_VIEW_IMAGE_LAYER_SETTINGS)
        # Bacteria Layer dlg
        viewMenu.Append(ID_VIEW_BACTERIA_LAYER_SETTINGS, "Bacteria Layer Settings", 
                        "Shows a dialog for changing bacteria rendering settings")
        self.Bind(wx.EVT_MENU, self.OnViewBacteriaLayerSettings, 
                  id=ID_VIEW_BACTERIA_LAYER_SETTINGS)
        # Output Text Area
        self.itemVOut = wx.MenuItem(viewMenu, wx.NewId(), "View Output\tCtrl+D",
                                    "Shows any text output by ProkaryMetrics such as calculations")
        viewMenu.AppendItem(self.itemVOut)
        self.Bind(wx.EVT_MENU, self.OnViewOutput, id=self.itemVOut.GetId())
        
        # Menu Bar
        menuBar = wx.MenuBar()
        menuBar.Append(fileMenu, "File")
#        menuBar.Append(dataMenu, "Data")
        menuBar.Append(toolsMenu, "Tools")
        menuBar.Append(viewMenu, "View")
        self.SetMenuBar(menuBar)
        
        self.Sizer.Layout()
        self.Show(1)
    
    
    def AppendOutput(self, text):
        self.txtOutput.AppendText(text)
        self.txtOutput.AppendText("\n")

    #TODO: finish changing this over
    def setInteractionMode(self, vcam=True):
        status = "View Camera Mode" if vcam else "Capture Camera Mode"
        self.StatusBar.SetStatusText(status, 3)
        
    def setRecordingMode(self, flag=True):
        status = "Recording Mode" if flag else "Exploring Mode"
        self.StatusBar.SetStatusText(status, 2)
        
    def setPickerPosition(self, loc):
        self.StatusBar.SetStatusText("(%.2f, %.2f, %.2f)" % (loc.x, loc.y, loc.z), 1)
    
    def setMainStatus(self, status):
        self.StatusBar.SetStatusText(status, 0)
        
    def ShowImageLayerSelect(self):
        if not self.pnlIBCRender.firstRender:
            dlg = SelectImageLayerDialog(self, self.pnlIBCRender)
            dlg.Show()
        else:
            wx.MessageBox("Please load an image set first", "Error", wx.ICON_ERROR | wx.OK)
        
    def ShowRenderSettings(self):
        if len(DataStore.ImageSets()) > 0:
            dlg = IBCSettingsDialog(self, self.pnlIBCRender.ImageLayer, self.setMainStatus)
            dlg.Show()
        else:
            wx.MessageBox("Please load an image set first", "Error", wx.ICON_ERROR | wx.OK)
            
    def ShowBacteriaLayerSettings(self):
        dlg = BacteriaLayerSettingsDialog(self, self.pnlIBCRender.BacteriaLayer, self.setMainStatus)
        dlg.Show()
        
    def AddImageSet(self, imgReader, ID=None):
        ID = DataStore.AddImageSet(IBCColor, imgReader.FilePaths, ID)
        self.pnlIBCRender.RenderImageData(ID, imgReader)        
        if ID is None:
            self.ShowRenderSettings()
        
    
    # EVENT HANDLERS
    def OnOpen(self, event):
        """
        Opens a set z-stack image files, and attempts to load them for 3D rendering
        """
        formats = '|'.join([cls.FileExtensionsDescriptor() for cls in imageIOTypes.Available]) 
        
        dlg = wx.FileDialog(self, "Choose a set of files", "", "", formats, 
                            wx.FD_OPEN|wx.FD_MULTIPLE|wx.FD_CHANGE_DIR|wx.FD_FILE_MUST_EXIST)
        if dlg.ShowModal() == wx.ID_OK and dlg.Paths:
            imgReader = imageIOTypes.Available[dlg.FilterIndex](dlg.Paths)
            self.AddImageSet(imgReader)
        
        dlg.Destroy()
        
    
    def OnSaveProject(self, event):
        dlg = wx.FileDialog(self, "Save project to file", "", "", "*.pkm", wx.FD_SAVE|wx.FD_OVERWRITE_PROMPT)
        if dlg.ShowModal() == wx.ID_OK and dlg.Filename:
            if not '.pkm' in dlg.Filename:
                dlg.Path = dlg.Path + '.pkm'
                
            # gather settings
            s = {}
            # used to be image-set
            s['image-set-ids'] = DataStore.ImageSets().keys()
            for isid in DataStore.ImageSets():
                s['img-%i' % isid] = self.pnlIBCRender.GetImageLayerByID(isid).Settings
            
            s['bacteria-layer-settings'] = self.pnlIBCRender.BacteriaLayer.Settings

            dio.saveProject(dlg.Path, s)
            self.StatusBar.SetStatusText("Project saved to %s" % dlg.Path, 0)
        
        dlg.Destroy()
    
    def OnLoadProject(self, event):
        if len(DataStore.ImageSets()) > 0:
            dlgWarn = wx.MessageDialog(self, """This action will overwrite \
                                       currently loaded data.\n\nContinue \
                                       anyway?""", 'Warning', wx.YES_NO | 
                                       wx.NO_DEFAULT | wx.ICON_WARNING)
            if dlgWarn.ShowModal() == wx.ID_NO:
                dlgWarn.Destroy()
                return
            dlgWarn.Destroy()

        formats = "ProkaryMetrics Project File (*.pkm)|*.pkm"
        dlg = wx.FileDialog(self, "Select saved project", "", "", formats, 
                            wx.FD_OPEN|wx.FD_CHANGE_DIR)
        if dlg.ShowModal() == wx.ID_OK and dlg.Filename:
            settings = dio.loadProject(dlg.Path)
            
            bactLayerSettings = None
            if 'bacteria-layer-settings' in settings:
                bactLayerSettings = settings['bacteria-layer-settings']
            
            # temp backwards compatibility
            idArray = settings['image-set-ids'] if 'image-set-ids' in settings else settings['image-set']
            
            for imgSetID in idArray:
                imgSettings = settings['img-%i' % imgSetID]
                paths = dio.testPaths(DataStore.ImageSets()[imgSetID].filepaths)
                if not paths:
                    wx.MessageBox("The project could not be loaded.", 
                                  "Error Loading Project", 
                                  wx.OK|wx.ICON_INFORMATION)
                    return
                
                # get correct file reader by stored file extension
                ftype = os.path.splitext(DataStore.ImageSets()[imgSetID].filepaths[0])[1]
                readerClass = imageIOTypes.GetReaderByType(ftype)
                imgReader = readerClass(DataStore.GetImageSet(imgSetID).filepaths)
                self.AddImageSet(imgReader, imgSetID)
                self.pnlIBCRender.GetImageLayerByID(imgSetID).Settings = imgSettings
            
            if bactLayerSettings:
                self.pnlIBCRender.BacteriaLayer.Settings = bactLayerSettings
            
            for ID in DataStore.ImageSets():
                self.pnlIBCRender.RenderImageData(ID, imgReader)
            
            # render recorded items
            self.pnlIBCRender.RenderStoredBacteria()
            self.pnlIBCRender.RenderStoredMarkers()
            
            self.pnlActions.UpdateBacteriaCount()
            
            self.pnlIBCRender.iren.Render()
            self.StatusBar.SetStatusText("Project loaded from %s" % dlg.Path, 0)
            
        dlg.Destroy()
        
    def OnExport(self, event):
        if DataStore.IsEmpty():
            wx.MessageBox("There are no data to export", "", wx.ICON_INFORMATION | wx.OK)
            return
        
        dispatch = {ID_EXPORT_BACTERIA: self.OnExportBacteria,
                    ID_EXPORT_LENGTHS: self.OnExportLengths,
                    ID_EXPORT_ORIENTATIONS: self.OnExportOrients}
        
        dispatch[event.Id]()
        
    
    def OnExportBacteria(self):
        dlg = wx.FileDialog(self, "Export recorded bacteria", "", "", "*.csv", wx.FD_SAVE|wx.FD_OVERWRITE_PROMPT)
        if dlg.ShowModal() == wx.ID_OK and dlg.Filename:
            if not '.csv' in dlg.Filename:
                dlg.Path = dlg.Path + '.csv'
            dio.exportBacteria(dlg.Path)
            self.StatusBar.SetStatusText("File exported to %s" % dlg.Path, 0)
    
        dlg.Destroy()
        
    def OnExportLengths(self):
        dlg = wx.FileDialog(self, "Export lengths of recorded bacteria", "", "", "*.csv", wx.FD_SAVE|wx.FD_OVERWRITE_PROMPT)
        if dlg.ShowModal() == wx.ID_OK and dlg.Filename:
            if not '.csv' in dlg.Filename:
                dlg.Path = dlg.Path + '.csv'
            dio.exportLengths(dlg.Path)
            self.StatusBar.SetStatusText("File exported to %s" % dlg.Path, 0)
        
        dlg.Destroy()
            
    def OnExportOrients(self):
        dlg = wx.FileDialog(self, "Export orientation data for recorded bacteria", "", "", "*.csv", wx.FD_SAVE|wx.FD_OVERWRITE_PROMPT)
        if dlg.ShowModal() == wx.ID_OK and dlg.Filename:
            if not '.csv' in dlg.Filename:
                dlg.Path = dlg.Path + '.csv'
            dio.exportOrientations(dlg.Path)
            self.StatusBar.SetStatusText("File exported to %s" % dlg.Path, 0)
        
        dlg.Destroy()
        
        



    # TOOLS MENU

#    def OnDynGauss(self, event):
#        dlg = wx.DirDialog(self, "Choose temporary storage directory", "")
#        
#        if dlg.ShowModal() == wx.ID_OK:
#            dynamicGaussian(DataStore.GetImageSet(0).filepaths, dlg.Path)
#        dlg.Destroy()
        
    def OnFitEllipsoid(self, event):
        mve = False
        if event.GetId() == ID_FIT_MVE_ELLIPSOID:
            mve = True
        self.pnlIBCRender.RenderFittedEllipsoid(mve=mve)
        self.toolsToggleEVis.Enable(True)
    
    def OnToggleEllipsoidVis(self, event):
        self.pnlIBCRender.ToggleEllipsoidVisibility()
        
    def OnCalcOrientation(self, event):
        self.pnlIBCRender.CalculateOrientations()
    
    def OnColorByOrientation(self, event):
        evtID = event.GetId()
        
        if evtID == ID_RGB:
            scheme = Vec3f(0,1,2)
        if evtID == ID_GBR:
            scheme = Vec3f(1,2,0)
        if evtID == ID_BGR:
            scheme = Vec3f(2,1,0)
            
        self.pnlIBCRender.ColorByOrientation(scheme)
        
    def OnCalcCommDensity(self, event):
        self.pnlIBCRender.CalculateCommunityDensity()    
    
    def TakeScreenshot(self, event):
        fmts = export.exportClasses.keys()
        dlg = wx.FileDialog(self, "Take Screenshot", "", "", 
                            export.exportFormats, wx.FD_SAVE)
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            fileSplit = dlg.GetFilename().split('.')
            if (fileSplit[len(fileSplit)-1].lower() not in fmts):
                path += '.'+fmts[dlg.GetFilterIndex()]
                
#            self.pnlIBCRender.switchCameras()
            export.saveScreen(path, fmts[dlg.GetFilterIndex()], 
                              self.pnlIBCRender.iren.GetRenderWindow())
            self.setMainStatus("Figure saved to "+path)
#            self.pnlIBCRender.switchCameras()
        
        dlg.Destroy()
        
#    def CapturePosition(self, event):
#        dlg = wx.FileDialog(self, "Save data position", "", "", 
#                            "*.npz", wx.FD_SAVE)
#        if dlg.ShowModal() == wx.ID_OK:
#            path = dlg.GetPath()
#            
#            bactMatrices = self.pnlIBCRender.BacteriaLayer().CaptureBacteriaTransforms()
#            imgMatrix = self.pnlIBCRender.ImageLayer().CaptureTransformMatrix()
            
            
            
            
            
            
            
            
            
        
    # VIEW MENU
    def OnSelectImageLayer(self, event):
        self.ShowImageLayerSelect()            
    
    def OnViewImageLayerSettings(self, event):
        self.ShowRenderSettings()
        
    def OnViewBacteriaLayerSettings(self, event):
        self.ShowBacteriaLayerSettings()
        
    def OnViewOutput(self, event):
        if self.txtOutput.IsShown():
            self.itemVOut.Text = "View Output\tCtrl+D"
            self.txtOutput.Hide()
        else:
            self.txtOutput.Show()
            self.itemVOut.Text = "Hide Output\tCtrl+D"
            
        self.Sizer.Layout()
        #TODO: this is horrible
        self.SetSize((self.GetSize().width, self.GetSize().height+1))
        self.SetSize((self.GetSize().width, self.GetSize().height-1))
        
        self.Refresh()
        self.Update()
        



    def OnMenuExit(self, event):
        """
        Handles window exit event
        """
        self.Close(True)
        
        


if __name__ == '__main__':
    app = wx.PySimpleApp()
    frame = MainWindow(None, -1, "ProkaryMetrics")
    app.MainLoop()
    sys.exit(0)