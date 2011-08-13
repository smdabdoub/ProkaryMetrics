'''
Created on Jul 24, 2011

@author: shareef
'''
from store import DataStore
from vector import Vec3f
import numpy as np
import scipy as s
import scipy.stats as ss
from collections import namedtuple

import csv

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


def communityOrientationStats(angle=True):
    """
    Calculate the orientation of all bacilli as an angle from each of the Euclidean 
    basis vectors in R^3 or just the dot product.
    
    :@rtype: tuple
    :@return: 
    """
    angles = [[],[],[]]
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
            
            if angle:
                angles[0].append(xbasis.angle(v))
                angles[1].append(ybasis.angle(v))
                angles[2].append(zbasis.angle(v))
            else:
                dotprods[0].append(xbasis.dot(v))
                dotprods[1].append(ybasis.dot(v))
                dotprods[2].append(zbasis.dot(v))
        # calculate filament orientations b/t each two markers
        if blen > 2:
            filaments.append(DataStore.BacteriaActors()[i])
            for i in range(blen):
                pass
                
            
            
    
#    data = np.hstack((np.array(angles).T, np.array(lengths)[:,np.newaxis]))
#    
#    with open('out.csv', 'w') as e:
#        writer = csv.writer(e, delimiter=',')
#        writer.writerow(['x','y','z','len'])
#        writer.writerows(data)

    if angle:
        return (generateDescriptiveStats(angles[0]),
                generateDescriptiveStats(angles[1]),
                generateDescriptiveStats(angles[2]))
    else:
        return assemblies, dotprods

    
def generateDescriptiveStats(data):
    return DescriptiveStats(s.mean(data), 
                            s.median(data), 
                            s.std(data), 
                            ss.scoreatpercentile(data, 25),
                            ss.scoreatpercentile(data, 75))
    
    
    
    
    
    
    