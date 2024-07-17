"""Creates the windows event filter allowing for suppression of windows events"""
from pynput import keyboard

_WM_INPUTLANGCHANGE = 0x0051
_WM_KEYDOWN = 0x0100
_WM_KEYUP = 0x0101
_WM_SYSKEYDOWN = 0x0104
_WM_SYSKEYUP = 0x0105
_PRESS_MESSAGES = (_WM_KEYDOWN, _WM_SYSKEYDOWN)
_RELEASE_MESSAGES = (_WM_KEYUP, _WM_SYSKEYUP)


def make_keyboard_filter_converter(**kwargs):
	"""Returns a function that can be used as a win32_event_filter for the keyboard listener.
	Takes on_press and on_release functions as kwargs.
	We invoke on_press and on_release in here, because the natural pynput listener callbacks
	do not allow for suppression."""

	def keyboard_filter_converter(msg, data):
		if msg in _PRESS_MESSAGES:
			key = keyboard.KeyCode.from_vk(data.vkCode)
			if key is None:
				return True
			try:
				key = keyboard.Key(key)
			except ValueError:
				pass
			if "on_press" in kwargs:
				should_suppress = kwargs["on_press"](key)
		elif msg in _RELEASE_MESSAGES:
			key = keyboard.KeyCode.from_vk(data.vkCode)
			if key is None:
				return True
			try:
				key = keyboard.Key(key)
			except ValueError:
				pass
			if "on_release" in kwargs:
				should_suppress = kwargs["on_release"](key)
		if should_suppress:
			keyboard.Listener.suppress_event(None)
		return True

	return keyboard_filter_converter
