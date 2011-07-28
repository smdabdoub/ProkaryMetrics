'''
Created on Apr 7, 2011

@author: Shareef Dabdoub
'''
from .base import VolumeImageReader
import vtk

class VolumeJPEGReader(VolumeImageReader):
    def __init__(self, filepaths):
        VolumeImageReader.__init__(self, filepaths)
        self.reader = vtk.vtkJPEGReader()
    
    @property
    def JPEGReader(self):
        return self.reader
    
    @classmethod
    def FileExtensionsDescriptor(cls):
        # cheap way
        #return 'JPEG Images|*.jpg;*.jpeg;*.JPG;*.JPEG'
        # dynamic way
        descriptor = 'JPEG Images'
        extensions = vtk.vtkJPEGReader().GetFileExtensions().split(' ')
        extensions.extend([item.upper() for item in extensions])
        extensions = ['*'+item for item in extensions]
        
        return '|'.join([descriptor, ';'.join(extensions)])
    
    @classmethod
    def FileExtensions(cls):
        extensions = vtk.vtkJPEGReader().GetFileExtensions().split(' ')
        extensions.extend([item.upper() for item in extensions])
        return extensions
















