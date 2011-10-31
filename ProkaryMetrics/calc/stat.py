'''
Created on Jul 24, 2011

@author: shareef
'''
from data.io import writeCSV
from store import DataStore
from vector import Vec3f
import numpy as np
import scipy as s
import scipy.stats as ss
from collections import namedtuple

DescriptiveStats = namedtuple('DescriptiveStats', 'mean med std q1 q3')

HFF = 2.86
ds = Vec3f(0.1,0.1,0.56)

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

    
    writeCSV(np.vstack(dist), ['dist'], 'density.csv')

    return generateDescriptiveStats(dist)


def communityOrientationStats():
    """
    Calculate the orientation of all bacilli as the dot product from each of the Euclidean 
    basis vectors in R^3.
    
    :@rtype: tuple
    :@return: 
    """
    dotprods = [[],[],[]]
    bacilli = []
    filaments = []
    lengths = []
    xbasis = Vec3f(1,0,0)
    ybasis = Vec3f(0,1,0)
    zbasis = Vec3f(0,0,1)
    
    for i, bact in enumerate(DataStore.Bacteria()):
        blen = len(bact.Markers)
        if blen == 2:
            bacilli.append(DataStore.BacteriaActors()[i])
            v = bact.Markers[0] - bact.Markers[1]
            lengths.append(v.length())
            v.normalize()
            dotprods[0].append(xbasis.dot(v))
            dotprods[1].append(ybasis.dot(v))
            dotprods[2].append(zbasis.dot(v))
        # calculate filament orientations b/t each two markers
        if blen > 2:
            filaments.append(i)
            for j in range(blen-1):
                v = bact.Markers[j] - bact.Markers[j+1]
                v.normalize()
                dotprods[0].append(xbasis.dot(v))
                dotprods[1].append(ybasis.dot(v))
                dotprods[2].append(zbasis.dot(v))
            
            
    
#    data = np.hstack((np.array(angles).T, np.array(lengths)[:,np.newaxis]))
#    writeCSV(data, ['x','y','z','len'], 'olen.csv')

    return bacilli, filaments, dotprods

    
def generateDescriptiveStats(data):
    return DescriptiveStats(s.mean(data), 
                            s.median(data), 
                            s.std(data), 
                            ss.scoreatpercentile(data, 25),
                            ss.scoreatpercentile(data, 75))
    
    
    
    
    
    
    