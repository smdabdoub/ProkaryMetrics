'''
Created on Apr 6, 2011

@author: shareef
'''
import Image
import vtk

class VolumeImageReader(object):
    def __init__(self, filepaths):
        """
        @type filenames: list
        @param filenames: The list of image filenames to open as a volume
        """
        self.reader = None
        self.filepaths = filepaths
        xmax, ymax = getImageSize(filepaths[0])
        self.pixelExtents = (0, xmax, 0, ymax)
        self.sliceRange = None
        self.dataSpacing = None
        
        self.imageArray = vtk.vtkStringArray()
        for fname in filepaths:
            self.imageArray.InsertNextValue(fname)

        
    def LoadVTKReader(self, dataSpacing, sliceRange=None):
        """
        @rtype vtkImageReader2
        @return: The supplied image files loaded as a volume into an 
                 appropriate vtk image container
        """
        self.dataSpacing = dataSpacing

        if sliceRange is None:
            self.sliceRange = (0, len(self.filepaths)-1)
        else:
            self.sliceRange = sliceRange
        
        self.reader.SetFileNames(self.imageArray)
        self.reader.SetDataExtent(self.pixelExtents[0],
                                      self.pixelExtents[1],
                                      self.pixelExtents[2],
                                      self.pixelExtents[3],
                                      self.sliceRange[0],
                                      self.sliceRange[1])
        self.reader.SetDataByteOrderToLittleEndian() 
        self.reader.SetDataSpacing(self.dataSpacing)
        
        return self.reader
    
    @property
    def VolumeExtents(self):
        """
        Returns a list containing the data extents in 3 dimensions
        
        :@rtype: list
        :@return: 6D list of data extents
        """
        ext = list(self.pixelExtents)
        ext.extend(self.sliceRange)
        return ext
    
    @property
    def VolumeReader(self):
        """
        :@rtype: vtk.vtkImageReader2
        """
        return self.reader
    
    @property
    def FilePaths(self):
        return self.filepaths
    
    @classmethod
    def FileExtensions(cls):
        pass


def getImageSize(fname):
    """
    Use the Python Imaging Library (PIL) to find the size of a 2D image.
    
    @type fname: string
    @param fname: The name of the image file
    @rtype: tuple
    @return: The number of pixels in the x and y dimensions of the image.
    """
    im = Image.open(fname)
    return im.size
    