'''
Created on Aug 12, 2011

@author: Shareef Dabdoub
'''
from store import DataStore

import numpy as np
import vtk
import wx


def NoBacteria():
    if DataStore.IsEmpty():
        wx.MessageBox("There are no recorded bacteria", "Error", wx.ICON_ERROR | wx.OK)
        return True
    return False

def CopyMatrix4x4(matrix):
    """
    Copies the elements of a vtkMatrix4x4 into a numpy array.
    
    :@type matrix: vtk.vtkMatrix4x4
    :@param matrix: The matrix to be copied into an array.
    :@rtype: numpy.ndarray
    """
    m = np.ones((4,4))
    for i in range(4):
        for j in range(4):
            m[i,j] = matrix.GetElement(i,j)
    return m

def StoreAsMatrix4x4(marray):
    """
    Copies the elements of a numpy array into a vtkMatrix4x4.
    
    :@type: numpy.ndarray
    :@param matrix: The array to be copied into a matrix.
    :@rtype matrix: vtk.vtkMatrix4x4
    """
    m = vtk.Matrix4x4()
    for i in range(4):
        for j in range(4):
            m.SetElement(i, j, marray[i,j])
    return m