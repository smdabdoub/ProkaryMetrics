'''
Created on Jun 24, 2011

@author: Shareef Dabdoub

Export image data to disk
'''
import vtk

exportClasses = {'bmp': vtk.vtkBMPWriter, 'jpg': vtk.vtkJPEGWriter, 
               'png': vtk.vtkPNGWriter, 'pnm': vtk.vtkPNMWriter, 
               'ps':  vtk.vtkPostScriptWriter, 'tiff': vtk.vtkTIFFWriter}

exportFormats = '|'.join(['BMP (*.bmp)|*.bmp', 'JPG (*.JPG)|*.jpg', 
                          'PNG (*.png)|*.png', 'PNM (*.pnm)|*.pnm', 
                          'PostScript (*.ps)|*.ps', 'TIFF (*.tiff)|*.tiff'])

def saveScreen(path, type, renWin):
    imageFilter = vtk.vtkWindowToImageFilter()
    imageFilter.SetInput(renWin)
    imageFilter.Modified()

    imageWriter = exportClasses[type]()
    imageWriter.SetInput(imageFilter.GetOutput())
    imageWriter.SetFileName(path)
    imageWriter.Write()
