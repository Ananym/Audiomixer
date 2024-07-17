"""Main script.  Sets up threads and connects up the event loop."""
import threading
from queue import Queue

from config import load_config
from event_handler import EventHandler, EventHandlerEndReason
from indicator import VolumeIndicator
from listeners import ActivatorState, KeyboardHandler, MouseHandler
from tray_icon import SystemTrayIcon

if __name__ == "__main__":
	print("Audiomixer starting...")

	while True:
		# enables reload config by restarting loop
		config = load_config()
		event_queue = Queue()
		tray_icon = SystemTrayIcon(event_queue)
		indicator = VolumeIndicator(config)

		activator_state = ActivatorState(config.activatorHotkey, event_queue)
		kb_handler = KeyboardHandler(event_queue, config, activator_state)
		mouse_handler = MouseHandler(event_queue, activator_state)

		event_handler = EventHandler(event_queue, config, indicator)

		with kb_handler as kl, mouse_handler as ml, tray_icon as ti:
			threading.Thread(target=event_handler.start_event_loop).start()
			indicator.start()
			# indicator loop will continue until closed by an exit event in the handler
			if event_handler.end_reason == EventHandlerEndReason.EXIT_REQUESTED:
				break
