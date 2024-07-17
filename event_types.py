"""event types"""

from typing import NamedTuple


class ScrollEvent(NamedTuple):
    """scroll event"""

    x: float
    y: float
    magnitude: int


class ActivatorKeyPressEvent(NamedTuple):
    """activator key press event"""


class MiddleMouseEvent(NamedTuple):
    """middle mouse event"""

    x: float
    y: float


class ActivatorReleaseEvent(NamedTuple):
    """hotkey release event"""


class ExitRequestedEvent(NamedTuple):
    """exit event"""


class CursorMoveEvent(NamedTuple):
    """cursor move event"""

    x: float
    y: float


class KeyIncrementEvent(NamedTuple):
    """key increment event"""


class KeyDecrementEvent(NamedTuple):
    """key decrement event"""


class KeyMuteToggleEvent(NamedTuple):
    """key mute toggle event"""


class RestartRequestedEvent(NamedTuple):
    """restart event"""
