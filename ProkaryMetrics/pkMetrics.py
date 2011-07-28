from data.io import saveProject, loadProject, exportData, dynamicGaussian
from data.imageIO import export
import data.imageIO.types as imageIOTypes
from render.basic import GreenColor
from render.ibc import IBCSettingsDialog
from render.bacteria import BacteriaLayerSettingsDialog
from settings import RenderActionsPanel
from store import DataStore
from vtkRender import IBCRenderPanel

import wx
import os.path
import sys

# CONSTANTS
ID_OPEN = wx.NewId()
ID_LOAD_PROJECT = wx.NewId()
ID_SAVE_PROJECT = wx.NewId()
ID_EXPORT = wx.NewId()

ID_DYNGAUSS = wx.NewId()

ID_FIT_ELLIPSOID = wx.NewId()
ID_TOGGLE_ELLIPSOID_VIS = wx.NewId()

ID_VIEW_IMAGE_LAYER_SETTINGS = wx.NewId()
ID_VIEW_BACTERIA_LAYER_SETTINGS = wx.NewId()


class MainWindow(wx.Frame):
    """
    Main display window for the project.
    """
    
    def __init__(self,parent,id,title):
        wx.Frame.__init__(self, parent, wx.ID_ANY, title, size=(800,700))
        self.Center(direction=wx.HORIZONTAL)

        # Set up status bar
        self.StatusBar = self.CreateStatusBar(4)
        self.StatusBar.SetStatusWidths([-3, -1, -1, -1])
        self.StatusBar.SetStatusStyles([wx.SB_NORMAL, wx.SB_NORMAL, wx.SB_RAISED, wx.SB_RAISED])

        self.Sizer = wx.BoxSizer(wx.VERTICAL)
        self.pnlIBCRender = IBCRenderPanel(self, imode_callback=self.setInteractionMode, 
                                                 rmode_callback=self.setRecordingMode, 
                                                 ppos_callback=self.setPickerPosition)
        self.pnlActions =  RenderActionsPanel(self, self.pnlIBCRender, 
                                              status_callback=self.setMainStatus)
        
        self.Sizer.Add(self.pnlIBCRender, 1, wx.EXPAND | wx.BOTTOM, 10)
        self.Sizer.Add(self.pnlActions, 0, wx.EXPAND  | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)
        
        # File menu
        fileMenu = wx.Menu()
        # Open file
        fileMenu.Append(ID_OPEN, "Open File(s)...\tCtrl+O"," Open a file to edit")
        self.Bind(wx.EVT_MENU, self.OnOpen, id=ID_OPEN)
        # Load project
        fileMenu.Append(ID_LOAD_PROJECT, "Load Project...\tCtrl+L"," Open a file to edit")
        self.Bind(wx.EVT_MENU, self.OnLoadProject, id=ID_LOAD_PROJECT)
        # Save project
        fileMenu.Append(ID_SAVE_PROJECT, "Save Project...\tCtrl+S"," Open a file to edit")
        self.Bind(wx.EVT_MENU, self.OnSaveProject, id=ID_SAVE_PROJECT)
        # Export Bacteria
        fileMenu.Append(ID_EXPORT, "Export Bacteria...\tCtrl+E"," Open a file to edit")
        self.Bind(wx.EVT_MENU, self.OnExport, id=ID_EXPORT)
        # Exit
        item = fileMenu.Append(wx.ID_EXIT,"E&xit"," Terminate the program")
        self.Bind(wx.EVT_MENU, self.OnMenuExit, item)
        
        # Data menu
        dataMenu = wx.Menu()
        dataMenu.Append(ID_DYNGAUSS, "Convert to PPM...", 
        "Convert loaded image set to PPM files for use with the Dynamic Gaussian algorithm.")
        self.Bind(wx.EVT_MENU, self.OnDynGauss, id=ID_DYNGAUSS)
        
        # Tools menu
        toolsMenu = wx.Menu()
        toolsMenu.Append(ID_FIT_ELLIPSOID, "Fit Ellipsoid to IBC", 
                         """Use the existing recorded bacteria to fit an \
                         ellipsoid for estimation of volume and general \
                         shape""")
        self.Bind(wx.EVT_MENU, self.OnFitEllipsoid, id=ID_FIT_ELLIPSOID)
        self.toolsToggleEVis = wx.MenuItem(toolsMenu, ID_TOGGLE_ELLIPSOID_VIS, 
                                      "Toggle Ellipsoid Visibility")
        self.toolsToggleEVis.Enable(False)
        toolsMenu.AppendItem(self.toolsToggleEVis)
        self.Bind(wx.EVT_MENU, self.OnToggleEllipsoidVis, id=ID_TOGGLE_ELLIPSOID_VIS)
        toolsScreenshot = wx.MenuItem(toolsMenu, wx.NewId(), 'Take Screenshot',
                                      """Saves the contents of the display \
                                      window to an image file""")
        toolsMenu.AppendItem(toolsScreenshot)
        self.Bind(wx.EVT_MENU, self.TakeScreenshot, id=toolsScreenshot.GetId())
        
        # View menu
        viewMenu = wx.Menu()
        viewMenu.Append(ID_VIEW_IMAGE_LAYER_SETTINGS, "Image Layer Settings", 
                        "Shows a dialog for changing image rendering settings")
        self.Bind(wx.EVT_MENU, self.OnViewImageLayerSettings, 
                  id=ID_VIEW_IMAGE_LAYER_SETTINGS)
        viewMenu.Append(ID_VIEW_BACTERIA_LAYER_SETTINGS, "Bacteria Layer Settings", 
                        "Shows a dialog for changing bacteria rendering settings")
        self.Bind(wx.EVT_MENU, self.OnViewBacteriaLayerSettings, 
                  id=ID_VIEW_BACTERIA_LAYER_SETTINGS)
        
        # Menu Bar
        menuBar = wx.MenuBar()
        menuBar.Append(fileMenu, "File")
#        menuBar.Append(dataMenu, "Data")
        menuBar.Append(toolsMenu, "Tools")
        menuBar.Append(viewMenu, "View")
        self.SetMenuBar(menuBar)
        
        # apparently necessary on OSX to force everything to draw
        self.Sizer.Layout()
        self.Show(1)


    def setInteractionMode(self, trackball=True):
        status = "Trackball Mode" if trackball else "Joystick Mode"
        self.StatusBar.SetStatusText(status, 3)
        
    def setRecordingMode(self, flag=True):
        status = "Recording Mode" if flag else "Exploring Mode"
        self.StatusBar.SetStatusText(status, 2)
        
    def setPickerPosition(self, loc):
        self.StatusBar.SetStatusText("(%.2f, %.2f, %.2f)" % (loc.x, loc.y, loc.z), 1)
    
    def setMainStatus(self, status):
        self.StatusBar.SetStatusText(status, 0)
        
    def ShowRenderSettings(self):
        if len(DataStore.ImageSets()) > 0:
            dlg = IBCSettingsDialog(self, self.pnlIBCRender.ImageLayer, self.setMainStatus)
            dlg.Show()
        else:
            wx.MessageBox("Please load an image set first", "Error", wx.ICON_ERROR | wx.OK)
            
    def ShowBacteriaLayerSettings(self):
        dlg = BacteriaLayerSettingsDialog(self, self.pnlIBCRender.BacteriaLayer, self.setMainStatus)
        dlg.Show()
        
    #TODO: generalize for multiple image sets
    def AddImageSet(self, imgReader):
        id = DataStore.AddImageSet(GreenColor, imgReader.FilePaths)
        self.pnlIBCRender.RenderImageData(id, imgReader)        
        self.ShowRenderSettings()
        
    
    # EVENT HANDLERS
    def OnOpen(self, event):
        """
        Opens a set z-stack image files, and attempts to load them for 3D rendering
        """
        if DataStore.ImageSets():
            wx.MessageBox("Currently, only one volumetric image set may be loaded.", "", wx.OK|wx.ICON_INFORMATION)
            return
        
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
            ibcSett = self.pnlIBCRender.ImageLayer.Settings
            s['image-sets'] = [ibcSett['ImageSetID']]
            s['img-%i' % ibcSett['ImageSetID']] = ibcSett
            s['bacteria-layer-settings'] = self.pnlIBCRender.BacteriaLayer.Settings

            saveProject(dlg.Path, s)
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
            settings = loadProject(dlg.Path)
            # for now, only one image set is possible
            imgSettings = settings['img-%i' % settings['image-sets'][0]]
            imgSetID = imgSettings['ImageSetID']
            
            bactLayerSettings = None
            if 'bacteria-layer-settings' in settings:
                bactLayerSettings = settings['bacteria-layer-settings']
            
            # validate the directory of the stored image paths
            paths = DataStore.ImageSets()[imgSetID].filepaths
            if not os.path.exists(os.path.split(paths[0])[0]):
                wx.MessageBox("""The path to the images stored in the project \
                              does not exist. Please choose the current folder \
                              where the files exist.""", "Error Loading Project", 
                              wx.OK|wx.ICON_ERROR)
                cdDlg = wx.DirDialog(self, "Locate project image files",
                                     "", wx.DD_DIR_MUST_EXIST|wx.DD_CHANGE_DIR)
        
                if cdDlg.ShowModal() == wx.ID_OK:
                    #TODO: should check new full path is correct
                    # strip off the file name and prepend the new dir
                    for i in range(len(paths)):
                        paths[i] = os.path.join(cdDlg.Path, os.path.split(paths[i])[1])
                else:
                    wx.MessageBox("The project could not be loaded.", "Error Loading Project", 
                                  wx.OK|wx.ICON_INFORMATION)
                    cdDlg.Destroy()
                    return

                cdDlg.Destroy()
            
            
            # get correct file reader by stored file extension
            ftype = os.path.splitext(DataStore.ImageSets()[imgSetID].filepaths[0])[1]
            readerClass = imageIOTypes.GetReaderByType(ftype)
            imgReader = readerClass(DataStore.GetImageSet(imgSetID).filepaths)
            self.pnlIBCRender.ImageLayer.Settings = imgSettings
            self.pnlIBCRender.ImageLayer.ImageReader = imgReader
            
            if bactLayerSettings:
                self.pnlIBCRender.BacteriaLayer.Settings = bactLayerSettings
            
            for id in DataStore.ImageSets():
                self.pnlIBCRender.RenderImageData(id, imgReader)
            
            # render recorded bacteria
            self.pnlIBCRender.RenderStoredBacteria()
            
            self.pnlActions.UpdateBacteriaCount()
            
            self.pnlIBCRender.iren.Render()
            self.StatusBar.SetStatusText("Project loaded from %s" % dlg.Path, 0)
            
        dlg.Destroy()
        
    
    def OnExport(self, event):
        dlg = wx.FileDialog(self, "Export recorded bacteria", "", "", "*.csv", wx.FD_SAVE|wx.FD_OVERWRITE_PROMPT)
        if dlg.ShowModal() == wx.ID_OK and dlg.Filename:
            if not '.csv' in dlg.Filename:
                dlg.Path = dlg.Path + '.csv'
            
            exportData(dlg.Path)

        dlg.Destroy()


    # TOOLS MENU

    def OnDynGauss(self, event):
        dlg = wx.DirDialog(self, "Choose temporary storage directory", "")
        
        if dlg.ShowModal() == wx.ID_OK:
            dynamicGaussian(DataStore.GetImageSet(0).filepaths, dlg.Path)

        dlg.Destroy()
        
    def OnFitEllipsoid(self, event):
        self.pnlIBCRender.RenderFittedEllipsoid()
        self.toolsToggleEVis.Enable(True)
    
    def OnToggleEllipsoidVis(self, event):
        self.pnlIBCRender.ToggleEllipsoidVisibility()
        
    def TakeScreenshot(self, event):
        fmts = sorted(export.exportClasses.keys())
        dlg = wx.FileDialog(self, "Take Screenshot", "", "", 
                            export.exportFormats, wx.FD_SAVE)
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            fileSplit = dlg.GetFilename().split('.')
            if (fileSplit[len(fileSplit)-1].lower() not in fmts):
                path += '.'+fmts[dlg.GetFilterIndex()]
            export.saveScreen(path, fmts[dlg.GetFilterIndex()], 
                              self.pnlIBCRender.iren.GetRenderWindow())
            self.setMainStatus("Figure saved to "+path)
        
        dlg.Destroy()
    
        
    # VIEW MENU
    def OnViewImageLayerSettings(self, event):
        self.ShowRenderSettings()
        
    def OnViewBacteriaLayerSettings(self, event):
        self.ShowBacteriaLayerSettings()



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