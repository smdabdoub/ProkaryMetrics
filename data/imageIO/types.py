'''
Created on Apr 7, 2011

@author: Shareef Dabdoub

This module is a repository for available image loading classes
'''
from tiff import VolumeTIFFReader
from jpeg import VolumeJPEGReader

Available = [VolumeTIFFReader, VolumeJPEGReader]

def GetReaderByType(ftype):
    for rClass in Available:
        if ftype in rClass.FileExtensions():
            return rClass
    raise TypeError