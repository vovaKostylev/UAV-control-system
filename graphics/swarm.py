from UAV import *
import math
from eventbus import *
class Swarm():
    def __init__(self, scene, coord):
        self.uavs = list()
        for i in coord:
            self.uavs.append(UAV(x = i[0],y = i[1], model = 'circle' , scene = scene))

    def highlight_leader_tracer(self):
        self.uavs[0].highlight_tracer()


    def shutdown_all(self):


        for i in self.uavs:
            self._shutdown(i)
    def _shutdown(self, uav: UAV):
        uav.block_movement()


    def complete_mission(self):
        self.shutdown_all()
        self.highlight_leader_tracer()