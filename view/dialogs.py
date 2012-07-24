'''
Created on March 5, 2012

@author: Shareef Dabdoub
'''
from store import DataStore

import os.path as osp
import wx

class SelectImageLayerDialog(wx.Dialog):
    def __init__(self, parent, pnlIBCRender, title='Select Image Layer', **kwargs):
        wx.Dialog.__init__(self, parent, size=(275,200), title=title, 
                           style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER, **kwargs)

        self.pnlIBCRender = pnlIBCRender
        
        # grab current selection from pnlIBCRender
        self.currID = self.pnlIBCRender.CISID
        
        # create a list of file path representations, one for each image set
        self.imgSetNames = []
        self.imgSetDict = {}

        for imgsetID in DataStore.ImageSets():
            paths = DataStore.GetImageSet(imgsetID).filepaths
            name = self.pnlIBCRender.GetImageLayerByID(imgsetID).name
            if name == "":
                name = osp.split(osp.commonprefix(paths))[1] + '*'
            name = str(imgsetID) + ": " + name
            self.imgSetNames.append(name)
            self.imgSetDict[name] = imgsetID
            if imgsetID == self.currID:
                self.currName = name
        
        # Dialog control setup
        self.Sizer = wx.BoxSizer(wx.VERTICAL)
        
        self.lbImgSets = wx.ListBox(self, wx.ID_ANY, choices=self.imgSetNames, style=wx.LB_SINGLE)
        self.Bind(wx.EVT_LISTBOX, self._lbImgSets_click, id=self.lbImgSets.Id)
        self.Sizer.Add(self.lbImgSets, 1, wx.EXPAND | wx.ALIGN_CENTER | wx.TOP | wx.LEFT | wx.RIGHT, 10)
        
        self.lbImgSets.SetStringSelection(self.currName)

        
    def _lbImgSets_click(self, events):
        selection = self.lbImgSets.GetStringSelection()
        imgsetID = self.imgSetDict[selection]
        self.pnlIBCRender.SetCurrentImageLayer(imgsetID)