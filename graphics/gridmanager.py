from ursina import *
import math
import random
import sys

from eventbus import *
from windowstatemanager import *


try:
    from scene import Swarm, Targets
except ImportError as e:
    print(f"Ошибка импорта scene: {e}")
    sys.exit(1)

# === ГЛОБАЛЬНЫЕ НАСТРОЙКИ ===
AREA_WIDTH = 100
AREA_HEIGHT = 60
VIEW_RADIUS = 6
GRID_STEP = 1.0
MAX_ENTITIES = 500
frame_counter = 0
class GridManager:
    def __init__(self, area_width, area_height, view_radius):
        self.min_x = -area_width / 2
        self.max_x = area_width / 2
        self.min_y = -area_height / 2
        self.max_y = area_height / 2
        self.view_radius = view_radius
        self.grid_step = GRID_STEP
        self.grid_width = int(area_width / self.grid_step)
        self.grid_height = int(area_height / self.grid_step)
        self.total_cells = self.grid_width * self.grid_height

        self.visited_positions = set()
        self.cell_entities = {}
        self.cell_density = {}




        print(f"Сетка: {self.grid_width}x{self.grid_height}, всего ячеек: {self.total_cells}")

    def distance_2d(self, p1, p2):
        return math.sqrt((p1.x - p2.x) ** 2 + (p1.y - p2.y) ** 2)

    def count_neighbors(self, i, j):
        count = 0
        for di in range(-2, 3):
            for dj in range(-2, 3):
                ni, nj = i + di, j + dj
                if (ni, nj) in self.cell_entities and (ni, nj) != (i, j):
                    count += 1
        return count

    def update_density(self, key):
        i, j = key
        self.cell_density[key] = self.count_neighbors(i, j)
        for di in range(-2, 3):
            for dj in range(-2, 3):
                ni, nj = i + di, j + dj
                neighbor_key = (ni, nj)
                if neighbor_key in self.cell_entities and neighbor_key != key:
                    self.cell_density[neighbor_key] = self.count_neighbors(ni, nj)

    def mark_visited(self, position, paint=False):
        try:
            x, y = position.x, position.y
        except AttributeError:
            print(f"Ошибка: position не имеет x/y: {position}")
            return

        i0 = int((x - self.min_x) / self.grid_step)
        j0 = int((y - self.min_y) / self.grid_step)
        cells_in_radius = int(self.view_radius / self.grid_step) + 1
        new_cells = []

        for i in range(max(0, i0 - cells_in_radius), min(self.grid_width, i0 + cells_in_radius + 1)):
            for j in range(max(0, j0 - cells_in_radius), min(self.grid_height, j0 + cells_in_radius + 1)):
                cx = self.min_x + (i + 0.5) * self.grid_step
                cy = self.min_y + (j + 0.5) * self.grid_step
                if self.distance_2d(position, Vec2(cx, cy)) <= self.view_radius:
                    key = (i, j)
                    if key not in self.visited_positions:
                        self.visited_positions.add(key)
                        new_cells.append(key)

        if paint and new_cells:
            for key in new_cells:
                i, j = key
                cx = self.min_x + (i + 0.5) * self.grid_step
                cy = self.min_y + (j + 0.5) * self.grid_step
                entity = Entity(
                    model='quad',
                    position=(cx, cy, 0.5),
                    scale=self.grid_step * 0.9,
                    color=color.rgba(0, 255, 100, 255)
                )
                self.cell_entities[key] = entity
                self.update_density(key)

            if len(self.cell_entities) > MAX_ENTITIES:
                max_density = max(self.cell_density.values())
                dense_keys = [k for k, v in self.cell_density.items() if v == max_density]
                key_to_remove = random.choice(dense_keys)
                if key_to_remove in self.cell_entities:
                    destroy(self.cell_entities[key_to_remove])
                    del self.cell_entities[key_to_remove]
                    del self.cell_density[key_to_remove]
                    i, j = key_to_remove
                    for di in range(-2, 3):
                        for dj in range(-2, 3):
                            ni, nj = i + di, j + dj
                            neighbor_key = (ni, nj)
                            if neighbor_key in self.cell_entities:
                                self.cell_density[neighbor_key] = self.count_neighbors(ni, nj)

    def cleanup(self):
        for key, entity in self.cell_entities.items():
            destroy(entity)
        self.cell_entities.clear()
        self.cell_density.clear()



class DroneManager:
    def __init__(self, positions = None, coords = None, num_drones = 6):
        #self.scene = Targets(positions=positions)

        self.num_drones = num_drones or 4

        if positions is None:
            positions = [(random.uniform(-30, 30), random.uniform(-15, 15)) for _ in range(5)]
        self.scene = Targets(positions=positions)

        if coords is None:
            coords = self._generate_initial_coords(self.num_drones)

        self.swarm = Swarm(coord=coords, scene=self.scene)
        self.uavs = self.swarm.uavs

        for uav in self.uavs:
            uav.trail = []

        event_bus.subscribe("window_closing", self.swarm.complete_mission)
    def _generate_initial_coords(self, n):
        """Генерирует стартовые координаты БПЛА"""
        coords = []
        spacing = 2.0
        for i in range(n):
            x = (i % 5) * spacing - 5
            y = (i // 5) * spacing - 5
            coords.append((x, y))
        return coords

    def update_drones(self, grid: GridManager):
        for uav in self.uavs:
            p1 = uav.last_position
            p2 = uav.position
            dx = p2.x - p1.x
            dy = p2.y - p1.y
            length = math.sqrt(dx ** 2 + dy ** 2)

            if length > 1.0:
                angle = math.degrees(math.atan2(dy, dx))
                trail_segment = Entity(model='quad',
                                       position=((p1.x + p2.x) / 2, (p1.y + p2.y) / 2, 0.02),
                                       scale=(length, 0.2),
                                       rotation_z=angle,
                                       color=color.green)
                uav.trail.append(trail_segment)
                if len(uav.trail) > 100:
                    destroy(uav.trail.pop(0))

            grid.mark_visited(uav.position, paint=True)


#if __name__ == '__main__':
   # app = Ursina()
  #  application.fps = 30





  #  app.run()
