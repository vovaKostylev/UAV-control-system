from graphics.scene  import *
from missionmanager import  *
app = Ursina(load_automatic_screenshots=False)


# Setting Camera View
camera.orthographic = True
camera.fov = max(AREA_WIDTH, AREA_HEIGHT) * 1.1
camera.position = (0, 0)
scene = Scene()
def update():
    scene.update()

app.run()
