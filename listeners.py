"""handles keyboard and mouse events"""
from threading import Lock
from pynput import keyboard, mouse
from event_types import (
	ScrollEvent,
	MiddleMouseEvent,
	ActivatorReleaseEvent,
	ExitRequestedEvent,
	CursorMoveEvent,
	KeyIncrementEvent,
	KeyDecrementEvent,
	KeyMuteToggleEvent,
)
from keycode_serde import deleftrightify
from keyboard_filter import make_keyboard_filter_converter
from config import Config


class ActivatorState:
	"""Tracks whether activators are pressed"""
	def __init__(self, activators, event_queue):
		self.activators = set(activators)
		self.pressed_activators = set()
		self.lock = Lock()
		self.event_queue = event_queue
		print(f"Activators: {self.activators}")

	def press(self, key):
		"""If the key is an activator, add it to the set of pressed activators"""
		if key in self.activators:
			with self.lock:
				self.pressed_activators.add(key)

	def release(self, key):
		"""If the key is an activator, remove it from the set of pressed activators"""
		if key in self.activators:
			was_active = self.is_active()
			with self.lock:
				self.pressed_activators.discard(key)
			if was_active:
				self.event_queue.put(ActivatorReleaseEvent())

	def is_active(self):
		"""all activators pressed"""
		with self.lock:
			return len(self.pressed_activators) == len(self.activators)

	def is_activator(self, key):
		"""whether key is an activator"""
		return key in self.activators


class KeyboardHandler:
	"""listens for activators and hotkey presses - this is a context manager"""
	def __init__(self, event_queue, config: Config, activator_state):
		self.event_queue = event_queue
		self.activator_state = activator_state
		self.events_for_vkeys = {
			config.incrementKey: KeyIncrementEvent(),
			config.decrementKey: KeyDecrementEvent(),
			config.muteToggleKey: KeyMuteToggleEvent(),
			config.exitKey: ExitRequestedEvent(),
		}
		# print(f"Binds: {self.events_for_vkeys}")
		self.listener = self._create_listener()

	def _create_listener(self):
		return keyboard.Listener(
			win32_event_filter=make_keyboard_filter_converter(
				on_press=self._on_press, on_release=self._on_release
			)
		)

	def _on_press(self, key):
		deleftrightified_key = deleftrightify(key)
		self.activator_state.press(deleftrightified_key)
		if not self.activator_state.is_active():
			return
		if not hasattr(key, "vk") or key.vk not in self.events_for_vkeys:
			return
		self.event_queue.put(self.events_for_vkeys[key.vk])
		return True

	def _on_release(self, key):
		deleftrightified_key = deleftrightify(key)
		self.activator_state.release(deleftrightified_key)
		return False

	def __enter__(self):
		self.listener.start()
		return self

	def __exit__(self, exc_type, exc_val, exc_tb):
		print("Exiting keyboard handler")
		self.listener.stop()

	def join(self):
		"""debug"""
		self.listener.start()
		self.listener.join()


class MouseHandler:
	"""listens for mouse scrolls and clicks during activation - context manager"""
	def __init__(self, event_queue, activator_state):
		self.event_queue = event_queue
		self.activator_state = activator_state
		self.listener = self._create_listener()

	def _create_listener(self):
		return mouse.Listener(
			on_scroll=self._on_scroll,
			on_click=self._on_click,
			on_move=self._on_move,
			suppress=False,
		)

	def _on_scroll(self, x, y, _, dy):
		if self.activator_state.is_active():
			self.event_queue.put(ScrollEvent(x, y, dy))
			self.listener.suppress_event()

	def _on_click(self, x, y, button, pressed):
		if self.activator_state.is_active():
			if pressed and button == mouse.Button.middle:
				self.event_queue.put(MiddleMouseEvent(x, y))
				self.listener.suppress_event()

	def _on_move(self, x, y):
		self.event_queue.put(CursorMoveEvent(x, y))

	def __enter__(self):
		self.listener.start()
		return self

	def __exit__(self, exc_type, exc_val, exc_tb):
		print("Exiting mouse handler")
		self.listener.stop()
