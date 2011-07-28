'''
Created on Dec 13, 2010

@author: Shareef Dabdoub
'''
from vector import Vec3f

class Bacterium(object):
    def __init__(self, markers):
        self._markers = [Vec3f(marker) for marker in markers]
        self._orientation = Vec3f(0,0,0)
        
        #TODO: figure out how to represent orientation for filaments (if that makes sense)
        if len(markers) == 1:
            self._orientation = Vec3f(0,0,0)
        elif len(markers) == 2:
            diff = self._markers[0] - self._markers[1]
            diff.normalize()
            self._orientation = diff
        elif len(markers) > 2:
            self._orientation = Vec3f(0,0,0)
        
    @property
    def Markers(self):
        return self._markers
    
    @property
    def Orientation(self):
        return self._orientation