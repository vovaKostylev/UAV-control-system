from UAV import  *

from math import *
class Camera():
    def __init__(self,scene, radius, position):
        self.scene = scene
        self.radius = radius
        self.position = position

    def scan(self):
        for i in self.scene.targets:
            if(self.distance(obj = i) <= self.radius):
                i.visible = True
                #print(i.x,i.y)
    def distance(self, obj):
         return sqrt((self.position.x - obj.x)**2  + ( self.position.y - obj.y)**2)


