'''
Created on Jan 19, 2011

@author: shareef
'''
from store import DataStore
from vector import Vec3f

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
    store['markers'] = [Vec3f(m.GetCenter()) for m in DataStore.Markers()]
    
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
        
    if 'markers' in store:
        for marker in store['markers']:
            DataStore.AddMarker(marker)
    
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
        











        
        
        
        