from os import path
import pystray
from PIL import Image

from event_types import ExitRequestedEvent, RestartRequestedEvent


class SystemTrayIcon:

    def __init__(self, event_queue):
        self.title = "Audio Mixer"
        self.icon = None
        self.event_queue = event_queue

    def _exit_app(self):
        self.event_queue.put(ExitRequestedEvent())

    def _reload_config(self):
        self.event_queue.put(RestartRequestedEvent())

    def __enter__(self):
        menu = pystray.Menu(
            pystray.MenuItem("Reload Config", self._reload_config),
            pystray.MenuItem("Exit", self._exit_app),
        )
        icon_path = path.join(path.dirname(__file__), "trayicon.ico")
        self.icon = pystray.Icon(self.title, Image.open(icon_path), self.title, menu)
        self.icon.run_detached()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.icon.stop()
        print("tray icon stopped")
