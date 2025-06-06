from ursina import *
import random
import sys
from eventbus import  *
from windowstatemanager import  *

try:
    from scene import Swarm, Targets
except ImportError as e:
    print(f"Ошибка импорта scene: {e}")
    sys.exit(1)

app = Ursina()
application.fps = 30  # Ограничиваем FPS




# === ПАРАМЕТРЫ ===
area_width = 100
area_height = 60
view_radius = 6
drone_speed = 5
num_drones = 4

# === ПЛОЩАДКА ===
Entity(model='quad', scale=(area_width, area_height), color=color.gray, z=1)

# Камера
camera.orthographic = True
camera.fov = max(area_width, area_height) * 1.1
camera.position = (0, 0)

# === ДРОНЫ ===
try:
    pos = [(0, 1), (10, 10)]
    scene = Targets(positions=pos)
    coords = [(0, 0), (1, 1), (2, 2), (-1, -1)]
    swarm = Swarm(coord=coords, scene=scene)
    event_bus.subscribe("window_closing", swarm.highlight_leader_tracer)
except Exception as e:
    print(f"Ошибка инициализации Swarm/Targets: {e}")
    sys.exit(1)

# Проверяем, есть ли uavs в swarm
if not hasattr(swarm, 'uavs') or not swarm.uavs:
    print("Ошибка: swarm.uavs пуст или не определён")
    sys.exit(1)

# Инициализируем следы для каждого дрона
for uav in swarm.uavs:
    uav.trail = []
    print(f"Инициализирован дрон с позицией: {uav.position}")

# === СЛЕД ===
visited_positions = set()
grid_step = 1.0
min_x = -area_width / 2
max_x = area_width / 2
min_y = -area_height / 2
max_y = area_height / 2
grid_width = int(area_width / grid_step)
grid_height = int(area_height / grid_step)
total_cells = grid_width * grid_height
print(f"Сетка: {grid_width}x{grid_height}, всего ячеек: {total_cells}")
WindowStateManager(event_bus)
# Хранилище для Entity ячеек и их густоты
cell_entities = {}  # key=(i,j), value=Entity
cell_density = {}  # key=(i,j), value=число соседей


def count_neighbors(i, j):
    """Подсчитывает количество соседних ячеек в радиусе 5x5"""
    count = 0
    for di in range(-2, 3):
        for dj in range(-2, 3):
            ni, nj = i + di, j + dj
            if (ni, nj) in cell_entities and (ni, nj) != (i, j):
                count += 1
    return count


def update_density(key):
    """Обновляет густоту для ячейки и её соседей"""
    i, j = key
    cell_density[key] = count_neighbors(i, j)
    # Обновляем соседей
    for di in range(-2, 3):
        for dj in range(-2, 3):
            ni, nj = i + di, j + dj
            neighbor_key = (ni, nj)
            if neighbor_key in cell_entities and neighbor_key != key:
                cell_density[neighbor_key] = count_neighbors(ni, nj)


def mark_visited(position, paint=False):
    try:
        x, y = position.x, position.y
    except AttributeError:
        print(f"Ошибка: position не имеет x/y: {position}")
        return

    i0 = int((x - min_x) / grid_step)
    j0 = int((y - min_y) / grid_step)
    cells_in_radius = int(view_radius / grid_step) + 1
    new_cells = []

    # Проверяем ячейки в радиусе
    for i in range(max(0, i0 - cells_in_radius), min(grid_width, i0 + cells_in_radius + 1)):
        for j in range(max(0, j0 - cells_in_radius), min(grid_height, j0 + cells_in_radius + 1)):
            cx = min_x + (i + 0.5) * grid_step
            cy = min_y + (j + 0.5) * grid_step
            if distance_2d(position, Vec2(cx, cy)) <= view_radius:
                key = (i, j)
                if key not in visited_positions:
                    visited_positions.add(key)
                    new_cells.append(key)

    # Создаем Entity для каждой новой ячейки
    if paint and new_cells:
        for key in new_cells:
            i, j = key
            cx = min_x + (i + 0.5) * grid_step
            cy = min_y + (j + 0.5) * grid_step
            entity = Entity(
                model='quad',
                position=(cx, cy, 0.5),  # z=0.5, чтобы быть выше площадки
                scale=grid_step * 0.9,
                color=color.rgba(0, 255, 100, 255)  # Полная непрозрачность
            )
            cell_entities[key] = entity
            update_density(key)
            print(f"Создан Entity для ячейки {key} на ({cx:.2f}, {cy:.2f}), густота: {cell_density[key]}")
        # Ограничиваем количество Entity (5000)
        max_entities = 500
        if len(cell_entities) > max_entities:
            # Находим ячейку с максимальной густотой
            max_density = max(cell_density.values())
            dense_keys = [k for k, v in cell_density.items() if v == max_density]
            key_to_remove = random.choice(dense_keys)
            if key_to_remove in cell_entities:
                destroy(cell_entities[key_to_remove])
                del cell_entities[key_to_remove]
                del cell_density[key_to_remove]
                # Обновляем густоту соседей
                i, j = key_to_remove
                for di in range(-2, 3):
                    for dj in range(-2, 3):
                        ni, nj = i + di, j + dj
                        neighbor_key = (ni, nj)
                        if neighbor_key in cell_entities:
                            cell_density[neighbor_key] = count_neighbors(ni, nj)
                print(f"Удалена ячейка {key_to_remove} с густотой {max_density} (всего Entity: {len(cell_entities)})")


# Обработчик закрытия окна



#window.exit_function = on_exit

frame_counter = 0


def update():
    global swarm, frame_counter
    frame_counter += 1
    # Отладка: выводим количество Entity
    if frame_counter % 10 == 0:
        print(f"Текущее количество Entity: {len(cell_entities)}")

    for i, uav in enumerate(swarm.uavs):
        try:
            p1 = uav.last_position
            p2 = uav.position
        except AttributeError as e:
            print(f"Ошибка: у дрона {i} отсутствует last_position или position: {e}")
            continue

        dx = p2.x - p1.x
        dy = p2.y - p1.y
        length = math.sqrt(dx ** 2 + dy ** 2)

        if length > 1.0:
            angle = math.degrees(math.atan2(dy, dx))
            trail_segment = Entity(
                model='quad',
                position=((p1.x + p2.x) / 2, (p1.y + p2.y) / 2, 0.02),
                scale=(length, 0.2),
                rotation_z=angle,
                color=color.green
            )
            uav.trail.append(trail_segment)
            if len(uav.trail) > 100:
                destroy(uav.trail.pop(0))

        # Вызываем mark_visited каждый кадр для всех дронов
        mark_visited(uav.position, paint=True)  # Все дроны закрашивают

    # Обновляем процент покрытия раз в 5 кадров
    if frame_counter % 5 == 0:
        coverage = min(100.0, len(visited_positions) / total_cells * 100)
        print(f'Обследовано: {coverage:.2f}%')
        if coverage >= 99.9:
            print("✅ Полное покрытие достигнуто! Завершение через 2 секунды.")
            invoke(application.quit, delay=2)


# Первичная отметка
for i, uav in enumerate(swarm.uavs):
    try:
        mark_visited(uav.position, paint=True)
    except AttributeError as e:
        print(f"Ошибка при первичной отметке дрона {i}: {e}")

app.run()

application.quit()