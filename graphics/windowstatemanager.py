from ursina import  *

class WindowStateManager:
    def __init__(self, event_bus):
        self.event_bus = event_bus
        #window.exit_button.on_click = self._on_exit_click
        self.original_quit = application.quit


        application.quit = self._on_exit_click

    def delayed(self):
        print("Закрытие окна")
    def _on_exit_click(self):
        print("[WindowStateManager] Закрытие окна инициировано")

        self.event_bus.emit("window_closing")
        self.event_bus.emit("screen")
        invoke(self.original_quit , delay = 5)





