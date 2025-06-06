from ursina import *
from camera import *
from Tracer import  *
class UAV(Entity):
    def update(self):
        if(self._movement_enable == True):
            self.move()
        self.camera.position = self.position
        self.camera.scan()
        self.last_position = self.position
        self.tracer.add_point(self.position)

    def __init__(self, scene, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.camera = Camera(scene= scene, radius=5, position=  self.position)
        self.last_position = self.position
        self.tracer = Tracer()
        self._movement_enable = True

    def move(self):
        self.x -= held_keys['a'] * time.dt * 40
        self.x += held_keys['d'] * time.dt * 40
        self.y -= held_keys['s'] * time.dt * 40
        self.y += held_keys['w'] * time.dt * 40

    def highlight_tracer(self):

        self.tracer.become_visible()

    def block_movement(self):
        self._movement_enable = False







