'''
Created on Jun 24, 2011

@author: Shareef Dabdoub

Export image data to disk
'''
from collections import OrderedDict
import vtk

exportClasses = OrderedDict([('png', vtk.vtkPNGWriter), ('jpg', vtk.vtkJPEGWriter), 
                            ('tiff', vtk.vtkTIFFWriter), ('pnm', vtk.vtkPNMWriter),
                            ('ps', vtk.vtkPostScriptWriter), ('bmp', vtk.vtkBMPWriter)])

exportFormats = '|'.join(['PNG (*.png)|*.png', 'JPG (*.JPG)|*.jpg', 
                          'TIFF (*.tiff)|*.tiff', 'PNM (*.pnm)|*.pnm', 
                          'PostScript (*.ps)|*.ps', 'BMP (*.bmp)|*.bmp'])

def saveScreen(path, type, renWin):
    imageFilter = vtk.vtkWindowToImageFilter()
    imageFilter.SetInput(renWin)
    imageFilter.Modified()

    imageWriter = exportClasses[type]()
    imageWriter.SetInput(imageFilter.GetOutput())
    imageWriter.SetFileName(path)
    imageWriter.Write()
