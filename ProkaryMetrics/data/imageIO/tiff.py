'''
Created on Apr 6, 2011

@author: shareef
'''
from .base import VolumeImageReader
import vtk

class VolumeTIFFReader(VolumeImageReader):
    def __init__(self, filepaths):
        VolumeImageReader.__init__(self, filepaths)
        self.reader = vtk.vtkTIFFReader()
    
    @property
    def TIFFReader(self):
        return self.reader
    
    #TODO: this should be partially generalized to the base class
    #TODO: it could call the base function and pass it the vtkTIFFReader class
    @classmethod
    def FileExtensionsDescriptor(cls):
        """
        Grab the acceptable variations on the file extension and return 
        in the format required by the wx system for file dialogs.
        """
        descriptor = 'TIFF Images'
        extensions = vtk.vtkTIFFReader().GetFileExtensions().split(' ')
        extensions.extend([item.upper() for item in extensions])
        extensions = ['*'+item for item in extensions]
        
        return '|'.join([descriptor, ';'.join(extensions)])

    @classmethod
    def FileExtensions(cls):
        extensions = vtk.vtkTIFFReader().GetFileExtensions().split(' ')
        extensions.extend([item.upper() for item in extensions])
        return extensions














