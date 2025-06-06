
from collections import defaultdict

class EventBus:
    def __init__(self):
        self.listeners = {}

    def subscribe(self, event_name, callback):
        self.listeners.setdefault(event_name, []).append(callback)

    def emit(self, event_name, *args, **kwargs):
        for cb in self.listeners.get(event_name, []):
            cb(*args, **kwargs)



    # Глобальный экземпляр
event_bus = EventBus()



