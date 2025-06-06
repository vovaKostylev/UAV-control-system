from ursina import *


class Detectable(Entity):
    def __init__(self,*args, **kwargs ):
        super().__init__(*args, **kwargs)
        self.visible = False


class Targets:
    def __init__(self, positions):
        self.targets = []
        for i in positions:
             self.targets.append(Detectable(x = i[0], y= i[1], model = 'circle', color = color.red ,collider = 'box', scale = (1,1)))

