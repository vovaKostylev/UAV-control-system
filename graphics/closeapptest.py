from ursina import *
from scene import *
from UAV import *
app = Ursina()

def on_exit():
    print("Попытка закрытия окна заблокирована!")
    return True  # Блокирует закрытие окна

#window.exit_button.on_click = on_exit

#scene  = Scene()
#uav = UAV(scene)

#uav.block_movement()


print(hasattr(window, 'exit_function'))
app.run()