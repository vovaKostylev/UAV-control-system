from ursina import *

class Map(Entity):
    def __init__(self, texture_path='map.png', scale=(20, 20)):
        super().__init__(
            model='quad',
            texture=load_texture(texture_path),
            scale=scale,
            position=(0, 0, 0)
        )

        camera.orthographic = True
        camera.fov = 10

        self.is_dragging = False
        self.last_mouse_pos = Vec2(0, 0)

    def update(self):
        if self.is_dragging:
            mouse_delta = mouse.position - self.last_mouse_pos
            camera.position -= Vec3(mouse_delta.x, mouse_delta.y, 0) * camera.fov
            self.last_mouse_pos = mouse.position

    def input(self, key):
        if key == 'left mouse down':
            self.is_dragging = True
            self.last_mouse_pos = mouse.position
        elif key == 'left mouse up':
            self.is_dragging = False

        if key in ('right mouse down', 'right mouse up'):
            return

        if key == 'scroll up':
            camera.fov -= 0.5
        elif key == 'scroll down':
            camera.fov += 0.5

        camera.fov = clamp(camera.fov, 2, 50)

