# 3D Vector Class
import math

class Vec2f(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def length(self):
        return math.sqrt( self.x*self.x + self.y*self.y )

    def normalize(self):
        ln = self.length();
        self.x /= ln
        self.y /= ln
        
    def scalarMult(self, f):
        self.x = self.x * f
        self.y = self.y * f
        
    ## OPERATOR REDEFINITIONS ##
    
    def __add__(self, other):
        if (isinstance(other, int) or isinstance(other, float)):
            return Vec2f(self.x + other, self.y + other)
        return Vec2f(self.x + other.x, self.y + other.y)
    
    def __sub__(self, other):
        if (isinstance(other, int) or isinstance(other, float)):
            return Vec2f(self.x - other, self.y - other)
        return Vec2f(self.x - other.x, self.y - other.y)
    
    def __rsub__(self, other):
        if (isinstance(other, int) or isinstance(other, float)):
            return Vec2f(other - self.x, other - self.y)
        return other.__sub__(self)
    
    def __neg__(self):
        return Vec2f(-self.x, -self.y)
        
    def __str__(self):
        return '<%f, %f>' % (self.x, self.y)
  
    def __repr__(self):
        return '<%f, %f>' % (self.x, self.y)

class Vec3f(object):
    def __init__(self, x=0, y=0, z=0):
        if isinstance(x, tuple) or isinstance(x, list):
            self.x = x[0]
            self.y = x[1]
            self.z = x[2]
        else:
            self.x = x
            self.y = y
            self.z = z
    
    def normalize(self):
        ln = self.length()
        self.x /= ln
        self.y /= ln
        self.z /= ln
    
    def length(self):
        return math.sqrt( self.x*self.x + self.y*self.y + self.z*self.z )
    
    def angle(self, other):
        """
        Calculates the angle between this and the other vector.
        dot(a,b) = len(a)*len(b)*cos(t)
        t = arccos(dot(a,b)/(len(a)*len(b))
        """ 
        return math.degrees(math.acos(self.dot(other)/(self.length()*other.length())))
    
    def dot(self, other):
        """Performs the dot product with the provided vector and returns a scalar"""
        return sum([self.x*other.x, self.y*other.y, self.z*other.z]) 
    
    def cross(self, other):
        """Performs the cross product with the provided vector and returns a new Vec3f"""
        return Vec3f(self.y*other.z - self.z*other.y, self.z*other.x - self.x*other.z, self.x*other.y - self.y*other.x)
    
    def midpoint(self, other):
        """Returns a new Vec3f that is the midpoint between the two"""
        x = (self.x + other.x) / 2;
        y = (self.y + other.y) / 2;
        z = (self.z + other.z) / 2;
        return Vec3f(x, y, z);

    def toTuple(self):
        return (self.x, self.y, self.z)
    # shift is a Vec2f
    def shiftYZ(self, shift):
        self.y = self.y + shift.x
        self.z = self.z + shift.y
        
    ## OPERATOR REDEFINITIONS ##
    
    def __add__(self, other):
        if (isinstance(other, int) or isinstance(other, float)):
            return Vec3f(self.x + other, self.y + other, self.z + other)
        return Vec3f(self.x + other.x, self.y + other.y, self.z + other.z)
    
    def __sub__(self, other):
        if (isinstance(other, int) or isinstance(other, float)):
            return Vec3f(self.x - other, self.y - other, self.z - other)
        return Vec3f(self.x - other.x, self.y - other.y, self.z - other.z)
    
    def __rsub__(self, other):
        if (isinstance(other, int) or isinstance(other, float)):
            return Vec3f(other - self.x, other - self.y, other - self.z)
        return other.__sub__(self)
    def __mul__(self, other):
        if (isinstance(other, int) or isinstance(other, float)):
            return Vec3f(self.x * other, self.y * other, self.z * other)
        if (isinstance(other, Vec3f)):
            return Vec3f(self.x * other.x, self.y * other.y, self.z * other.z)
        
    def __rmul__(self, other):
        return self.__mul__(other)
    
    def __neg__(self):
        return Vec3f(-self.x, -self.y, -self.z)
        
    def __str__(self):
        return '<%f, %f, %f>' % (self.x, self.y, self.z)
  
    def __repr__(self):
        return '<%f, %f, %f>' % (self.x, self.y, self.z)
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
