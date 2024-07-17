import tkinter as tk
from collections import namedtuple
from math import sqrt
from typing import Final
from enum import Enum
from config import Config

# Define named tuples for shapes
Circle = namedtuple("Circle", ["x", "y", "diameter"])
Rectangle = namedtuple("Rectangle", ["left", "top", "right", "bottom"])
Trapezoid = namedtuple(
	"Trapezoid",
	["x_left", "x_right", "y_topleft", "y_botleft", "y_topright", "y_botright"],
)
Arc = namedtuple("Arc", ["x", "top_y", "bottom_y", "curvature"])
MuteIcon = namedtuple("MuteIcon", ["left_x", "right_x", "top_y", "bottom_y"])


INNER_DIAMETER_RATIO: Final[float] = 5 / 6
RECTANGLE_HEIGHT_RATIO: Final[float] = 0.1
# ^ of outer diameter
TRAPEZOID_HEIGHT_RATIO: Final[float] = 1 / 3
# ^ of outer diameter
SPEAKER_WIDTH_RATIO: Final[float] = 0.15
# ^ of outer diameter
SPEAKER_COMPONENT_WIDTH_RATIO: Final[float] = 0.3819531
# ^ rect width / trap width
SPEAKER_HORIZONTAL_OFFSET_RATIO: Final[float] = 0.15
ARC_DISTANCE_FROM_SPEAKER_RATIO: Final[float] = 0.12
MUTE_DISTANCE_FROM_SPEAKER_RATIO: Final[float] = 0.10
MUTE_RATIO_TO_HEIGHT: Final[float] = 0.5
ARC_CURVATURE: Final[float] = -0.9


class OffsetMode(Enum):
	"""whether to use the cursor or window offset dimensions"""
	CURSOR = 0
	WINDOW = 1

class VolumeIndicator:
	"""Handles the indicator window and its functionality"""

	def __init__(self, config: Config):
		self.root = tk.Tk()
		self.root.withdraw()
		self.app_window = tk.Toplevel()
		self.app_window.overrideredirect(
			True
		)  # Removes the window border and title bar
		self.app_window.attributes("-topmost", True)  # Keeps the window on top
		self.app_window.attributes(
			"-transparentcolor", "#FF00FF"
		)  # Makes the specific color transparent
		self.outer_diameter = config.indicatorSize
		self.window_size = self.outer_diameter + 20
		self.app_window.geometry(f"{self.window_size}x{self.window_size}+800+400")
		self.app_window.withdraw()

		self.canvas = tk.Canvas(
			self.app_window,
			width=self.window_size,
			height=self.window_size,
			highlightthickness=0,
			bg="#FF00FF",
		)  # Use the same hex color for transparency
		self.canvas.pack()

		self.offset_x_cursor = config.indicatorXCursorOffset
		self.offset_y_cursor = config.indicatorYCursorOffset

		self.offset_x_window = config.indicatorXWindowOffset
		self.offset_y_window = config.indicatorYWindowOffset

		# Precalculate shapes
		self.outer_circle = Circle(0, 0, self.outer_diameter)
		self.inner_circle = self._calculate_inner_circle()
		self.speaker_rectangle = self._calculate_speaker_rectangle()
		self.speaker_trapezoid = self._calculate_speaker_trapezoid()
		self.volume_arc = self._calculate_volume_arc()
		self.mute_icon = self._calculate_mute_icon()

		self.volume_percentage = 0
		self.muted = False
		self.colour = config.indicatorColor

	def _calculate_inner_circle(self):
		inner_diameter = self.outer_diameter * INNER_DIAMETER_RATIO
		offset = (self.outer_diameter - inner_diameter) / 2
		return Circle(offset, offset, inner_diameter)

	def _calculate_speaker_rectangle(self):
		rectangle_height = self.outer_diameter * RECTANGLE_HEIGHT_RATIO
		speaker_width = self.outer_diameter * SPEAKER_WIDTH_RATIO
		speaker_horizontal_offset = (
			self.outer_diameter * SPEAKER_HORIZONTAL_OFFSET_RATIO
		)

		rect_width = speaker_width * SPEAKER_COMPONENT_WIDTH_RATIO

		rect_left = (self.outer_diameter / 2) - rect_width - speaker_horizontal_offset
		rect_top = (self.outer_diameter / 2) - (rectangle_height / 2)
		rect_bottom = (self.outer_diameter / 2) + (rectangle_height / 2)
		rect_right = self.outer_diameter / 2 - speaker_horizontal_offset
		return Rectangle(rect_left, rect_top, rect_right, rect_bottom)

	def _calculate_speaker_trapezoid(self):
		rectangle_height = self.outer_diameter * RECTANGLE_HEIGHT_RATIO
		trapezoid_height = self.outer_diameter * TRAPEZOID_HEIGHT_RATIO
		speaker_width = self.outer_diameter * SPEAKER_WIDTH_RATIO
		speaker_horizontal_offset = (
			self.outer_diameter * SPEAKER_HORIZONTAL_OFFSET_RATIO
		)
		trap_width = speaker_width * (1 - SPEAKER_WIDTH_RATIO)
		trap_x_left = self.outer_diameter / 2 - speaker_horizontal_offset
		trap_x_right = trap_width + self.outer_diameter / 2 - speaker_horizontal_offset
		trap_y_topleft = -rectangle_height / 2 + self.outer_diameter / 2
		trap_y_botleft = rectangle_height / 2 + self.outer_diameter / 2
		trap_y_topright = -trapezoid_height / 2 + self.outer_diameter / 2
		trap_y_botright = trapezoid_height / 2 + self.outer_diameter / 2
		return Trapezoid(
			trap_x_left,
			trap_x_right,
			trap_y_topleft,
			trap_y_botleft,
			trap_y_topright,
			trap_y_botright,
		)

	def _calculate_volume_arc(self):
		trapezoid_height = self.outer_diameter * TRAPEZOID_HEIGHT_RATIO
		speaker_width = self.outer_diameter * SPEAKER_WIDTH_RATIO
		speaker_horizontal_offset = (
			self.outer_diameter * SPEAKER_HORIZONTAL_OFFSET_RATIO
		)
		arc_x = (
			self.outer_diameter / 2
			+ speaker_width
			- speaker_horizontal_offset
			+ self.outer_diameter * ARC_DISTANCE_FROM_SPEAKER_RATIO
		)
		arc_top_y = -trapezoid_height / 2 + self.outer_diameter / 2
		arc_bottom_y = trapezoid_height / 2 + self.outer_diameter / 2
		return Arc(arc_x, arc_top_y, arc_bottom_y, ARC_CURVATURE)

	def _calculate_mute_icon(self):
		trapezoid_height = self.outer_diameter * TRAPEZOID_HEIGHT_RATIO
		speaker_width = self.outer_diameter * SPEAKER_WIDTH_RATIO
		speaker_horizontal_offset = (
			self.outer_diameter * SPEAKER_HORIZONTAL_OFFSET_RATIO
		)
		mute_size = trapezoid_height * MUTE_RATIO_TO_HEIGHT
		mute_left_x = (
			self.outer_diameter / 2
			+ speaker_width
			- speaker_horizontal_offset
			+ self.outer_diameter * MUTE_DISTANCE_FROM_SPEAKER_RATIO
		)
		mute_right_x = mute_left_x + mute_size
		mute_top_y = -mute_size / 2 + self.outer_diameter / 2
		mute_bottom_y = mute_size / 2 + self.outer_diameter / 2
		return MuteIcon(mute_left_x, mute_right_x, mute_top_y, mute_bottom_y)

	def _redraw(self, percentage, muted):
		self.canvas.delete("all") 

		self._draw_base_circle()
		self._draw_volume_arc(percentage)
		self._draw_inner_circle()
		self._draw_speaker()

		if muted:
			self._draw_mute_icon()
		else:
			self._draw_volume_arc_icon()

	def _draw_base_circle(self):
		self.canvas.create_oval(
			self.outer_circle.x,
			self.outer_circle.y,
			self.outer_circle.diameter,
			self.outer_circle.diameter,
			fill="black",
			outline="black",
		)

	def _draw_volume_arc(self, percentage):
		print(percentage)
		if percentage >= 0.99:
			self.canvas.create_oval(
				self.outer_circle.x,
				self.outer_circle.y,
				self.outer_circle.diameter,
				self.outer_circle.diameter,
				fill=self.colour,
				outline=self.colour,
			)
		elif percentage > 0.01:
			extent = 360 * percentage
			self.canvas.create_arc(
				self.outer_circle.x,
				self.outer_circle.y,
				self.outer_circle.diameter,
				self.outer_circle.diameter,
				start=90,
				extent=-extent,
				fill=self.colour,
				outline=self.colour,
				width=2,
			)

	def _draw_inner_circle(self):
		self.canvas.create_oval(
			self.inner_circle.x,
			self.inner_circle.y,
			self.inner_circle.x + self.inner_circle.diameter,
			self.inner_circle.y + self.inner_circle.diameter,
			fill="black",
			outline="black",
		)

	def _draw_speaker(self):
		# Rectangle
		self.canvas.create_polygon(
			self.speaker_rectangle.left,
			self.speaker_rectangle.top,
			self.speaker_rectangle.right,
			self.speaker_rectangle.top,
			self.speaker_rectangle.right,
			self.speaker_rectangle.bottom,
			self.speaker_rectangle.left,
			self.speaker_rectangle.bottom,
			fill=self.colour,
			outline=self.colour,
		)

		# Trapezoid
		self.canvas.create_polygon(
			self.speaker_trapezoid.x_left,
			self.speaker_trapezoid.y_topleft,
			self.speaker_trapezoid.x_right,
			self.speaker_trapezoid.y_topright,
			self.speaker_trapezoid.x_right,
			self.speaker_trapezoid.y_botright,
			self.speaker_trapezoid.x_left,
			self.speaker_trapezoid.y_botleft,
			fill=self.colour,
			outline=self.colour,
		)

	def _draw_mute_icon(self):
		self.canvas.create_line(
			self.mute_icon.left_x,
			self.mute_icon.top_y,
			self.mute_icon.right_x,
			self.mute_icon.bottom_y,
			fill=self.colour,
			width=3,
		)
		self.canvas.create_line(
			self.mute_icon.left_x,
			self.mute_icon.bottom_y,
			self.mute_icon.right_x,
			self.mute_icon.top_y,
			fill=self.colour,
			width=3,
		)

	def _draw_volume_arc_icon(self):
		self._draw_curved_line(
			self.canvas,
			self.volume_arc.x,
			self.volume_arc.top_y,
			self.volume_arc.x,
			self.volume_arc.bottom_y,
			self.volume_arc.curvature,
			self.colour,
			3,
		)

	def _draw_curved_line(
		self, canvas, start_x, start_y, end_x, end_y, curvature, colour, width
	):
		mid_x = (start_x + end_x) / 2
		mid_y = (start_y + end_y) / 2
		dx = end_x - start_x
		dy = end_y - start_y
		length = sqrt(dx**2 + dy**2)
		perp_dist = length * curvature / 2
		control_x = mid_x - perp_dist * dy / length
		control_y = mid_y + perp_dist * dx / length
		canvas.create_line(
			start_x,
			start_y,
			control_x,
			control_y,
			end_x,
			end_y,
			smooth=True,
			fill=colour,
			width=width,
		)

	def queue_update_indicator(self, percentage):
		"""Queue an update of the indicator's percentage."""
		self.volume_percentage = percentage
		self.app_window.after(0, self._redraw, percentage, self.muted)

	def queue_hide_indicator(self):
		"""Queue the hiding of the indicator."""
		self.app_window.after(0, self.app_window.withdraw)

	def _show_indicator(self, x, y, offset_mode: OffsetMode):
		offset_x = (
			self.offset_x_cursor
			if offset_mode == OffsetMode.CURSOR
			else self.offset_x_window
		)
		offset_y = (
			self.offset_y_cursor
			if offset_mode == OffsetMode.CURSOR
			else self.offset_y_window
		)
		self.app_window.geometry(f"+{x + offset_x}+{y + offset_y}")
		self.app_window.deiconify()

	def queue_show_indicator(self, x, y, offset_mode: OffsetMode):
		"""Queue the showing of the indicator."""
		self.app_window.after(0, self._show_indicator, x, y, offset_mode)

	def _move_indicator(self, x, y, offset_mode: OffsetMode):
		offset_x = (
			self.offset_x_cursor
			if offset_mode == OffsetMode.CURSOR
			else self.offset_x_window
		)
		offset_y = (
			self.offset_y_cursor
			if offset_mode == OffsetMode.CURSOR
			else self.offset_y_window
		)
		self.app_window.geometry(f"+{x + offset_x}+{y + offset_y}")

	def queue_move_indicator(self, x, y, offset_mode: OffsetMode):
		"""Queue the moving of the indicator."""
		self.app_window.after(0, self._move_indicator, x, y, offset_mode)

	def queue_set_mute(self, muted):
		"""Queue the setting of the mute state."""
		self.muted = muted
		self.app_window.after(0, self._redraw, self.volume_percentage, muted)

	def queue_close_root(self):
		"""Queue the closing of the root window."""
		print("destroying tkinter root")
		self.root.after(0, self.root.quit)

	def start(self):
		"""Run the indicator loop."""
		self.root.mainloop()
