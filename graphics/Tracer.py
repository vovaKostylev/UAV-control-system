import threading

from UAV import  *

from math import *
class Tracer():
    def __init__(self, color=color.green, thickness=0.1):
        self.color = color
        self.thickness = thickness
        self.last_point = None
        self.segments = []

        self.exit_flag = False


    def add_point(self, point):
        if self.last_point is None:
            self.last_point = point
            return

        # Вычисляем середину между точками
        mid = (self.last_point + point) / 2
        direction = point - self.last_point
        length = distance_2d(self.last_point, point)
        angle = math.degrees(math.atan2(direction.y, direction.x))

        # Создаём "отрезок"
        segment = Entity(
            model='quad',
            position=Vec3(mid.x, mid.y, 0.01),
            scale=(length, self.thickness),
            rotation_z=angle,
            color=self.color, visible = False
        )
        self.segments.append(segment)
        self.last_point = point

    def _on_exit_with_flash(self):
        # Prevent multiple exit attempts
        if self.exit_flag:
            return True

        print("Exit: Flashing tracer...")
        self.exit_flag = True

        # Show all segments (on main thread)


        # Schedule the delayed exit using Ursina's invoke (runs on main thread)
        invoke(self._delayed_exit, delay=5)

        # Block standard close
        return True

    def become_visible(self):

        for seg in self.segments:
            seg.visible = True


    def _delayed_exit(self):


        print("Exiting application")
        application.quit()  # Use Ursina's quit method