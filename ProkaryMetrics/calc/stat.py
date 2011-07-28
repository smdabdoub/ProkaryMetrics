'''
Created on Jul 24, 2011

@author: shareef
'''
from store import DataStore
from vector import Vec3f
import scipy as s
import scipy.stats as ss
from collections import namedtuple

DescriptiveStats = namedtuple('DescriptiveStats', 'mean med std q1 q3')

def communityDistanceStats():
    """
    Calculate DescriptiveStats for the distance between all bacteria (excluding filaments)
    """
    centers = []
    for bact in DataStore.Bacteria():
        blen = len(bact.Markers)
        if blen == 1:
            c = bact.Markers[0]
        elif blen == 2:
            c = bact.Markers[0].midpoint(bact.Markers[1])
        centers.append(c)
    
    dist = []
    for i in range(len(centers)-1):
        for j in range(i+1, len(centers)):
            dist.append((centers[i] - centers[j]).length())
    
    return generateDescriptiveStats(dist)


def communityOrientationStats():
    """
    Calculate the orientation of all bacilli as an angle from each of the Euclidean 
    basis vectors in R^3
    
    :@rtype: tuple
    :@return: 
    """
    angles = [[],[],[]]
    xbasis = Vec3f(1,0,0)
    ybasis = Vec3f(0,1,0)
    zbasis = Vec3f(0,0,1)
    
    for bact in DataStore.Bacteria():
        blen = len(bact.Markers)
        if blen == 2:
            v = (bact.Markers[1] - bact.Markers[1]).normalize()
            angles.append((xbasis.angle(v),
                          ybasis.angle(v),
                          zbasis.angle(v)))
    
    return (generateDescriptiveStats(angles[0]),
            generateDescriptiveStats(angles[1]),
            generateDescriptiveStats(angles[2]))

    
def generateDescriptiveStats(data):
    return DescriptiveStats(s.mean(data), 
                            s.median(data), 
                            s.std(data), 
                            ss.scoreatpercentile(data, 25),
                            ss.scoreatpercentile(data, 75))
    
    
    
    
    
    
    