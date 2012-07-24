'''
Created on Jul 24, 2011

@author: shareef
'''
from render.basic import generateSpline
from store import DataStore
from vector import Vec3f
import scipy as s
import scipy.stats as ss
from collections import namedtuple

#from data.io import writeCSV
#import numpy as np

DescriptiveStats = namedtuple('DescriptiveStats', 'mean med std q1 q3')

HFF = 2.86
ds = Vec3f(0.1,0.1,0.56)

def calculateLengths():
    """
    Calculate the lengths of all the recorded bacteria
    """
    lengths = []
    
    for _, bact in enumerate(DataStore.Bacteria()):
        blen = len(bact.Markers)
        if blen == 2:
            v = bact.Markers[0] - bact.Markers[1]
            lengths.append(str(v.length()))

        #TODO: calculate filament lengths
        if blen > 2:
            pass
    
    # if there are no bacteria, return
    if not lengths:
        return None
    
    return lengths


def communityDistanceStats():
    """
    Calculate DescriptiveStats for the distance between all bacteria (excluding filaments)
    """
    centers = []
    for bact in DataStore.Bacteria():
        blen = len(bact.Markers)
        if blen == 1:
            c = HFF*bact.Markers[0]*ds
        elif blen == 2:
            p1 = HFF*bact.Markers[0]*ds
            p2 = HFF*bact.Markers[1]*ds
            c = p1.midpoint(p2)
        else:
            continue
        centers.append(c)
    
    dist = []
    for i in range(len(centers)-1):
        for j in range(i+1, len(centers)):
            dist.append((centers[i] - centers[j]).length())

    
#    writeCSV(np.vstack(dist), ['dist'], 'density.csv')

    return generateDescriptiveStats(dist)


def communityOrientationStats():
    """
    Calculate the orientation of all bacilli as the dot product from each of the Euclidean 
    basis vectors in R^3.
    
    :@rtype: tuple
    :@return: 
    """
    bdots = [[],[],[]]
    fdots = [[],[],[]]
    sRes = []
    bacilli = []
    filaments = []
    #lengths = []
    xbasis = Vec3f(1,0,0)
    ybasis = Vec3f(0,1,0)
    zbasis = Vec3f(0,0,1)
    
    for i, bact in enumerate(DataStore.Bacteria()):
        blen = len(bact.Markers)
        if blen == 2:
            bacilli.append(DataStore.BacteriaActors()[i])
            v = bact.Markers[0] - bact.Markers[1]
            #lengths.append(v.length())
            v.normalize()
            bdots[0].append(xbasis.dot(v))
            bdots[1].append(ybasis.dot(v))
            bdots[2].append(zbasis.dot(v))
        # calculate filament orientations b/t each two markers
        if blen > 2:
            filaments.append(i)
            _, _, _, splinePoints = generateSpline(bact.Markers)
            sRes.append(len(splinePoints) - 1)  # -1 b/c we're using every pair, not every point
            sMarkers = [Vec3f(point) for point in splinePoints]
            for j in range(len(sMarkers)-1):
                v = sMarkers[j] - sMarkers[j+1]
                v.normalize()
                fdots[0].append(xbasis.dot(v))
                fdots[1].append(ybasis.dot(v))
                fdots[2].append(zbasis.dot(v))
            
            
    
#    data = np.hstack((np.array(angles).T, np.array(lengths)[:,np.newaxis]))
#    writeCSV(data, ['x','y','z','len'], 'olen.csv')

    return bacilli, filaments, bdots, fdots, sRes

    
def generateDescriptiveStats(data):
    return DescriptiveStats(s.mean(data), 
                            s.median(data), 
                            s.std(data), 
                            ss.scoreatpercentile(data, 25),
                            ss.scoreatpercentile(data, 75))
    
    
    
    
    
    
    