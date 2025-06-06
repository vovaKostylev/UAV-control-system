from gridmanager import *
from databasemanager import *
class MissionManager():

    def __init__(self):

        self.db = DatabaseManager()
        num_drones = self.db.get_init_data()
        self.grid = GridManager(AREA_WIDTH, AREA_HEIGHT, VIEW_RADIUS)
        self.drone_manager = DroneManager(num_drones = num_drones)
        WindowStateManager(event_bus)
        Entity(model='quad', scale=(AREA_WIDTH, AREA_HEIGHT), color=color.gray, z=1)
        self.frame_counter = 0
        event_bus.subscribe("window_closing", self.grid.cleanup)
        event_bus.subscribe("screen", self.db.complete_mission)


    #camera.orthographic = True
   # camera.fov = max(AREA_WIDTH, AREA_HEIGHT) * 1.1
    #camera.position = (0, 0)

    def update(self):
        for uav in self.drone_manager.uavs:
            self.grid.mark_visited(uav.position, paint=True)

        self.frame_counter += 1
        self.drone_manager.update_drones(self.grid)

        if self.frame_counter % 5 == 0:
            coverage = min(100.0, len(self.grid.visited_positions) / self.grid.total_cells * 100)
            print(f'Обследовано: {coverage:.2f}%')
            if coverage >= 99:
                print("✅ Полное покрытие достигнуто! Завершение через 2 секунды.")
                invoke(application.quit, delay= 0.1)