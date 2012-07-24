"""
This module contains classes used for storing rendering data.

@author: Shareef Dabdoub
@organization: The Ohio State University
@organization: Nationwide Children's Hospital
"""
from operator import itemgetter

class DataStore(object):
    """
    DataStore is meant to be used as a pseudo-database of bacteria and marker objects.
    
    This class provides only class-level members so that it can be used without
    defining a specific instance or location.
    """
    _markers = []
    _bacteriaActors = []
    _bacteria = []
    _imageSets = {}
    
    def __init__(self):
        pass
    
    @classmethod
    def AddMarker(cls, marker):
        """
        Adds a marker (sphere actor) instance to the store.
        
        @type data: vtkActor
        @param data: The newly placed marker to include in the store.
        """
        # add to the store 
        cls._markers.append(marker)
    
    @classmethod
    def ClearMarkers(cls):
        """
        Removes all markers instance at the specified index
        """
        cls._markers = []

    @classmethod
    def Markers(cls):
        """
        Retrieves all markers in the store.
        
        @rtype: list
        @return: A list containing all the markers currently in the store, 
                 i.e. corresponding to a bacterium
        """
        return cls._markers
    

    @classmethod
    def AddBacteriumActor(cls, prop):
        cls._bacteriaActors.append(prop)

    @classmethod
    def BacteriaActors(cls):
        return cls._bacteriaActors
        

    @classmethod
    def AddBacterium(cls, bact):
        cls._bacteria.append(bact)
    
    @classmethod
    def Bacteria(cls):
        return cls._bacteria
    
    @classmethod
    def BacteriaMarkers(cls):
        """
        Gathers the user-marked points for each bacterium into a 
        2D array (3xN) such that each column lists the x,y,z components
        for a single point.
        
        :@rtype: list
        :@return: A 2D list (3xN) where each row is an x,y,z component 
                  of a single point in 3D space corresponding to a 
                  user-marked point on a bacterium.
        """
        m = []
        for bact in cls._bacteria:
            m[0].extend([marker.x for marker in bact.Markers])
            m[1].extend([marker.y for marker in bact.Markers])
            m[2].extend([marker.z for marker in bact.Markers])
        
        return m
    
    @classmethod
    def IsEmpty(cls):
        if not cls._bacteria:
            return True
        return False
        
    @classmethod
    def AddImageSet(cls, color, filepaths, ID=None):
        if ID is None:
            if cls._imageSets:
                    ID = cls.sortImageSets()[-1][0] + 1
            else:
                ID = 0
        cls._imageSets[ID] = ImageSet(ID, color, filepaths)
        return ID
        
    @classmethod
    def GetImageSet(cls, ID):
        """
        Retrieves the ImageSet corresponding to the given ID.
        
        :@type id: int
        :@param id: The ID of the desired ImageSet
        :@rtype: ImageSet
        :@return: The ImageSet object with the matching ID.
        """
        if ID in cls._imageSets:
            return cls._imageSets[ID]
    
    @classmethod
    def ImageSets(cls):
        return cls._imageSets
    
    @classmethod
    def sortImageSets(cls):
        # sort the dict based on key
        return sorted(cls._imageSets.iteritems(), key=itemgetter(0))
        
        
        
        
        
        
class ImageSet(object):
    def __init__(self, ID, color, filepaths):
        self.id = ID
        self.color = color
        self.filepaths = filepaths
        
        
        
        
        
