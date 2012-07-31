'''
Created on Jan 19, 2011

@author: shareef
'''
from store import DataStore
from vector import Vec3f

import csv
from itertools import compress
import numpy as np
import os
import shelve
import wx

def saveProject(path, settings):
    """
    Save a representation of the system state: All the loaded image sets, 
    recorded bacteria, and render settings. This function uses the shelve
    module.
    """ 
    store = shelve.open(path)
    
    store['settings'] = settings
    store['imagesets'] = DataStore.ImageSets()
    store['bacteria'] = DataStore.Bacteria()
    store['markers'] = [Vec3f(m.GetCenter()) for m in DataStore.Markers()]
    
    store.close()
    
    
def loadProject(path):
    """
    Retrieve a saved project file and restore the user-created data.
    """
    store = shelve.open(path)
    
    for ID in store['imagesets']:
        imageset = store['imagesets'][ID]
        DataStore.AddImageSet(imageset.color, imageset.filepaths, imageset.id)
        
    for bacterium in store['bacteria']:
        DataStore.AddBacterium(bacterium)
        
    if 'markers' in store:
        for marker in store['markers']:
            DataStore.AddMarker(marker)
    
    settings = store['settings']
    store.close()
        
    return settings
        
        
        
def exportBacteria(path):
    """
    Export the recorded bacteria as a CSV containing the relevant information
    """
    f = open(path, 'w')
    
    try:
        writer = csv.writer(f, delimiter=',')
        
        for bacterium in DataStore.Bacteria():
            row = [len(bacterium.Markers)]
            # add the marker positions
            for loc in bacterium.Markers:
                row.extend([loc.x, loc.y, loc.z])
            row.extend(bacterium.Orientation.toTuple())
            
            writer.writerow(row)
    finally:
        f.close

def exportLengths(path):
    from calc.stat import calculateLengths
    lengths = calculateLengths()
    writeCSV([[l] for l in lengths], ['length'], path)
    
def exportOrientations(path):
    from calc.stat import communityOrientationStats
    _, _, bdots, _, _ = communityOrientationStats()
    # move data into [0...1] range
    bdots = [map(abs, bdots[i]) for i in range(3)]
    # bdots is 3 x n with X,Y,Z for each bacillus in one column, we want them as one row
    data = np.array(bdots).T
    writeCSV(data, ['x','y','z'], path)
        
        
def writeCSV(data, header, fname='out.csv'):
    """
    Takes a list/array of sequences and writes it to 
    disk as a CSV file.
    
    :@type data: list/array
    :@param data: Each entry must be a list/array even if there 
                  is only one element. e.g. [[1],[2],...].
    :@type header: list
    :@param header: The header row for the csv file with column names.
    :@type fname: str
    :@param fname: The filename to use when saving the output file.
                   '.csv' will be appended if not present.
    """
    if '.csv' != os.path.splitext(fname)[1]:
        fname += '.csv'
        
    with open(fname, 'w') as e:
        writer = csv.writer(e, delimiter=',')
        writer.writerow(header)
        writer.writerows(data)
        
        
def savePreferences():
    pass

def loadPreferences():
    pass
        


def testPaths(paths):
    """ 
    validate the directory of the stored image paths
    """
    def replacePathsDir(newPath, paths):
        return [os.path.join(newPath, os.path.split(p)[1]) for p in paths]
    
    def chooseDir():
        path = ""
        cdDlg = wx.DirDialog(None, "Locate project image files",
                             "", wx.DD_DIR_MUST_EXIST|wx.DD_CHANGE_DIR)
        if cdDlg.ShowModal() == wx.ID_OK:
            path = cdDlg.Path
        
        cdDlg.Destroy()
        return path
        
    # make sure the directory the files are supposed to be in actually exists
    if not os.path.exists(os.path.split(paths[0])[0]):
        wx.MessageBox("The path to the images stored in the project " +
                      "does not exist.\n\n Please select the folder " +
                      "containing the image data.", "Error Loading Project", 
                      wx.OK|wx.ICON_ERROR)
        

        newPath = chooseDir()
        if newPath: 
            paths = replacePathsDir(newPath, paths)
        else:
            return []

        
    
    needChecking = True
    # check that the files exist in the provided directory
    while needChecking:
        validFiles = [os.path.exists(p) for p in paths]
        # Some files exist
        if not all(validFiles):
            choice = wx.MessageBox("Some of the image files could not be found.\n\
                                   Click Yes to continue loading project, No to \
                                   choose a different directory.", 
                                   "Error Loading Project", 
                                   wx.YES_NO|wx.ICON_INFORMATION)
            if choice == wx.ID_YES:
                paths = compress(paths, validFiles)
                needChecking = False
            else:
                # whatever comes out of chooseDir will be checked next loop
                paths = replacePathsDir(chooseDir(), paths)
        # None of the files exist
        elif not any(validFiles):
            choice = wx.MessageBox("None of the image files could not be \
                                    found.\nClick OK to choose a different \
                                    directory, Cancel to stop loading the \
                                    project", 
                                   "Error Loading Project", 
                                   wx.OK|wx.CANCEL|wx.ICON_INFORMATION)
            if choice == wx.ID_OK:
                paths = replacePathsDir(chooseDir(), paths)
            else:
                paths = []
                needChecking = False
        else:
            needChecking = False
    
    return paths
    
        
#import subprocess
#def dynamicGaussian(imgPaths, tmpDir):
#    tmppaths = [os.path.join(tmpDir, os.path.split(img)[1]) for img in imgPaths]
#    newpaths = []
#    
#    # convert images to ppm
#    for i, path in enumerate(imgPaths):
#        newpaths.append(os.path.splitext(tmppaths[i])[0] + '.ppm')
#        args = ['/opt/local/bin/gm', 'convert', path, '-quality', '0', newpaths[i]]
#        print ' '.join(args)
#        try:
#            subprocess.call(args)
#        except OSError as ose:
#            print ose
#    
#    # run DG
#    dgpaths = []
#    for i, path in enumerate(newpaths):
#        split = list(os.path.splitext(path))
#        split.insert(-1, '_dg')
#        dgpaths.append(''.join(split))
#        args = ['/usr/bin/java', '-jar', '~/bin/dyngauss.jar', 
#                path, dgpaths[i], '1', '1', '25', '9']
#        try:
#            ret = subprocess.call(args)
#            print ret
#        except OSError as ose:
#            print ose
            
    # convert back to TIFF
#    for path in dgpaths:
        











        
        
        
        