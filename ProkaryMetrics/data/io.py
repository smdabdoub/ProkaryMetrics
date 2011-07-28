'''
Created on Jan 19, 2011

@author: shareef
'''
from store import DataStore

import csv
import os
import shelve

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
    
    store.close()
    
    
def loadProject(path):
    """
    Retrieve a saved project file and restore the user-created data.
    
    
    """
    store = shelve.open(path)
    
    for id in store['imagesets']:
        imageset = store['imagesets'][id]
        DataStore.AddImageSet(imageset.color, imageset.filepaths, imageset.id)
        
    for bacterium in store['bacteria']:
        DataStore.AddBacterium(bacterium)
    
    settings = store['settings']
    store.close()
        
    return settings
        
        
        
def exportData(path):
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
        
        
import subprocess
def dynamicGaussian(imgPaths, tmpDir):
    tmppaths = [os.path.join(tmpDir, os.path.split(img)[1]) for img in imgPaths]
    newpaths = []
    
    # convert images to ppm
    for i, path in enumerate(imgPaths):
        newpaths.append(os.path.splitext(tmppaths[i])[0] + '.ppm')
        args = ['/opt/local/bin/gm', 'convert', path, '-quality', '0', newpaths[i]]
        print ' '.join(args)
        try:
            subprocess.call(args)
        except OSError as ose:
            print ose
    
    # run DG
    dgpaths = []
    for i, path in enumerate(newpaths):
        split = list(os.path.splitext(path))
        split.insert(-1, '_dg')
        dgpaths.append(''.join(split))
        args = ['/usr/bin/java', '-jar', '~/bin/dyngauss.jar', 
                path, dgpaths[i], '1', '1', '25', '9']
        try:
            ret = subprocess.call(args)
            print ret
        except OSError as ose:
            print ose
            
    # convert back to TIFF
#    for path in dgpaths:
        











        
        
        
        