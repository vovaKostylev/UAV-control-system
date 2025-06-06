from swarm import *
from  objects import  *
from missionmanager  import  *

from eventbus import *
class Scene():

    def __init__(self):
        #self.pos = [(0,1) , (10,10)]
        #self.scene= Targets(positions= self.pos)
        #coords =  [(0,0), (1,1)]
        #self.swarm = Swarm(coord=  coords, scene = self.scene)
       self.missionmanager = MissionManager()


        #event_bus.subscribe("window_closing", self.swarm.highlight_leader_tracer )


    #def checkDistanse(self):
        #return sqrt((self.uav.x - self.car.x)**2  + ( self.uav.y - self.car.y)**2) <= 10
    def passObjects(self):
        pass
    def update(self):
        self.missionmanager.update() #self.uav.update()
       # if(self.checkDistanse() == True):
        #    self.car.visible = True


