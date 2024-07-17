"""Used for loading config"""

from pynput.keyboard import Key, KeyCode

from system_interactions import get_keycode_from_char

special_keycode_to_symbol_map = {
	Key.backspace: "backspace",
	Key.tab: "tab",
	Key.enter: "enter",
	Key.shift: "shift",
	Key.ctrl: "ctrl",
	Key.alt: "alt",
	Key.up: "up",
	Key.down: "down",
	Key.left: "left",
	Key.right: "right",
	Key.home: "home",
	Key.end: "end",
	Key.page_up: "pageup",
	Key.page_down: "pagedown",
	Key.insert: "insert",
	Key.delete: "delete",
	Key.caps_lock: "capslock",
	Key.esc: "esc",
	Key.f1: "f1",
	Key.f2: "f2",
	Key.f3: "f3",
	Key.f4: "f4",
	Key.f5: "f5",
	Key.f6: "f6",
	Key.f7: "f7",
	Key.f8: "f8",
	Key.f9: "f9",
	Key.f10: "f10",
	Key.f11: "f11",
	Key.f12: "f12",
	Key.cmd: "win",
	# Used as join separator
	KeyCode.from_char("+"): "plus",
}

symbol_to_special_keycode_map = {v: k for k, v in special_keycode_to_symbol_map.items()}

priority_order = [Key.ctrl, Key.shift, Key.alt, Key.cmd]


def keycode_to_symbol(keycode):
	"""Converts a keycode to a string symbol"""
	if keycode in special_keycode_to_symbol_map:
		return special_keycode_to_symbol_map[keycode]
	if keycode.char.isalpha():
		return keycode.char
	return None


def symbol_to_keycode(symbol):
	"""Converts a string symbol to a keycode"""
	if symbol in symbol_to_special_keycode_map:
		return symbol_to_special_keycode_map[symbol]
	try:
		ret = get_keycode_from_char(symbol)
		return ret
	except ValueError:
		return None


def string_to_keycode(string: str):
	"""Translates a single character string to a keycode"""
	ret = symbol_to_keycode(string[0])
	return ret


def sort_keycodes(keycodes):
	"""Rearranges keycodes to be presentable as hotkey string"""
	return sorted(
		keycodes,
		key=lambda keycode: (
			priority_order.index(keycode) if keycode in priority_order else 100
		),
	)


def keycodes_to_string(keycodes):
	"""Translates multiple keycodes to a joined string"""
	symbols = [keycode_to_symbol(keycode) for keycode in sort_keycodes(keycodes)]
	return "+".join(s for s in symbols if s is not None)


def string_to_keycodes(string):
	"""Translates a joined string into multiple keycodes"""
	keycodes = []
	for symbol in string.split("+"):
		keycode = symbol_to_keycode(symbol)
		if keycode is not None:
			keycodes.append(keycode)
		else:
			keycodes.append(KeyCode.from_char(symbol))
	return sort_keycodes(keycodes)


deleftrightifyMap = {
	Key.ctrl_l: Key.ctrl,
	Key.shift_l: Key.shift,
	Key.alt_l: Key.alt,
	Key.cmd_l: Key.cmd,
	Key.ctrl_r: Key.ctrl,
	Key.shift_r: Key.shift,
	Key.alt_r: Key.alt,
	Key.cmd_r: Key.cmd,
}


def deleftrightify(keycode):
	"""Converts shift_l to shift etc."""
	return deleftrightifyMap.get(keycode, keycode)


# def unshift(keycode : KeyCode):
# 	vk = keycode.vk
# 	scan_code = scan_code_for_vk(vk)
# 	unshifted = get_keycode_from_scan_code(scan_code)
# 	return unshifted

# def shift(keycode : KeyCode):
# 	return get_shifted_keycode(keycode)

ctrlshifta = string_to_keycodes("ctrl+shift+a")
assert ctrlshifta == [Key.ctrl, Key.shift, KeyCode.from_char("a")]
assert (
	keycodes_to_string([Key.ctrl, Key.shift, KeyCode.from_char("a")]) == "ctrl+shift+a"
)

# assert KeyCode.from_char("}") == get_shifted_keycode(KeyCode.from_char("]"))
# assert KeyCode.from_char("}") == get_shifted_keycode(KeyCode.from_char("}"))
