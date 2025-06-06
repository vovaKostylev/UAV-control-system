from ursina import *

app = Ursina()

# Загрузка текстуры карты
map_texture = load_texture('map_no_alpha.png')  # Укажи свой путь, если нужно

# Отображение карты
map_entity = Entity(
    model='quad',
    texture=map_texture,
    scale=(20, 20),
    position=(0, 0, 0)
)

camera.orthographic = True
camera.fov = 10  # начальный зум

is_dragging = False
last_mouse_pos = Vec2(0, 0)

def update():
    global last_mouse_pos
    if is_dragging:
        mouse_delta = mouse.position - last_mouse_pos
        camera.position -= Vec3(mouse_delta.x, mouse_delta.y, 0) * camera.fov
        last_mouse_pos = mouse.position

def input(key):
    global is_dragging, last_mouse_pos

    if key == 'left mouse down':
        is_dragging = True
        last_mouse_pos = mouse.position
    elif key == 'left mouse up':
        is_dragging = False

    # Игнорируем правую кнопку
    if key == 'right mouse down' or key == 'right mouse up':
        return

    # Зум колесиком мыши
    if key == 'scroll up':
        camera.fov -= 0.5
    elif key == 'scroll down':
        camera.fov += 0.5

    camera.fov = clamp(camera.fov, 2, 50)

# Убираем EditorCamera, если не нужен (он может реагировать на правую кнопку)
# EditorCamera()

app.run()
