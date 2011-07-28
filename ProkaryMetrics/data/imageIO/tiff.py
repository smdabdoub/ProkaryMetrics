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
    
    @classmethod
    def FileExtensionsDescriptor(cls):
        # cheap way
        #return 'TIFF Images|*.TIF;*.tif;*.tiff'
        # dynamic way
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














