'''
Created on Dec 20, 2010

@author: dabdoubs
'''
from store import DataStore
import wx

class RenderActionsPanel(wx.Panel):
    def __init__(self, parent, renderPanel, status_callback=None, **kwargs):
        wx.Panel.__init__(self, parent, **kwargs)

        self.renderPanel = renderPanel
        
        self.Sizer = wx.BoxSizer(wx.VERTICAL)
        self.lblSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.cmdSizer = wx.BoxSizer(wx.HORIZONTAL)
        
        # Labels
        self.lblRecordedBacteria = wx.StaticText(self, wx.ID_ANY, "0")
        self.lblSizer.Add(wx.StaticText(self, wx.ID_ANY, "Recorded Bacteria: "), 0, wx.ALIGN_CENTER)
        self.lblSizer.Add(self.lblRecordedBacteria, 0, wx.ALIGN_CENTER)
        self.Sizer.Add(self.lblSizer, 0, wx.ALIGN_CENTER | wx.BOTTOM, 5)
        
        # Buttons
        self.cmdRecord = wx.Button(self, wx.NewId(), "Record Bacterium")
        self.Bind(wx.EVT_BUTTON, self.cmdRecord_click, id=self.cmdRecord.Id)
        self.cmdUndo = wx.Button(self, wx.NewId(), "Undo")
        self.Bind(wx.EVT_BUTTON, self.cmdUndo_click, id=self.cmdUndo.Id)
        self.cmdSizer.Add(self.cmdRecord, 0, wx.ALIGN_RIGHT | wx.ALL, 5)
        self.cmdSizer.Add(self.cmdUndo, 0, wx.ALIGN_LEFT | wx.ALL, 5)
        
        self.Sizer.Add(self.cmdSizer, 0, wx.ALIGN_CENTER)

        
        
    # EVENT HANDLING    
    def cmdRecord_click(self, event):
        self.renderPanel.RecordBacterium()
        self.UpdateBacteriaCount()
        
    def cmdUndo_click(self, event):
        self.renderPanel.DeleteBacterium()
        self.UpdateBacteriaCount()
        
        
        
    def UpdateBacteriaCount(self):
        """
        Updates the visible count of recorded bacteria on the panel by 
        checking the DataStore. 
        """
        self.lblRecordedBacteria.Label = str(len(DataStore.Bacteria()))















