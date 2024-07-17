"""event handler"""

from enum import Enum

from config import Config
from event_types import (
    ActivatorReleaseEvent,
    CursorMoveEvent,
    ExitRequestedEvent,
    KeyDecrementEvent,
    KeyIncrementEvent,
    KeyMuteToggleEvent,
    MiddleMouseEvent,
    RestartRequestedEvent,
    ScrollEvent,
)
from indicator import VolumeIndicator, OffsetMode
from system_interactions import (
    adjust_volume_for_session,
    check_whether_session_muted,
    get_active_window_coordinates,
    get_session,
    get_active_window_pid,
    get_window_pid_at_location,
    toggle_mute,
    use_com_context,
)


class IndicatorState(Enum):
    """enum"""

    HIDDEN = 1
    MOUSE_LOCKED = 2
    WINDOW_LOCKED = 3


class EventHandlerEndReason(Enum):
    """enum"""

    EXIT_REQUESTED = 1
    RESTART_REQUESTED = 2


class EventHandler:
    """Listens and responds to events on the queue"""

    def __init__(self, event_queue, config: Config, indicator: VolumeIndicator):
        self.event_queue = event_queue
        self.state = IndicatorState.HIDDEN
        self.muted = False
        self.session_cache = {}
        self.volume_scale = config.scrollVolumeScale
        self.key_volume_diff = config.keyVolumeScale
        self.indicator = indicator
        self.end_reason = None
        self.current_session = None
        self.search_children_of_parents = config.searchChildrenOfParents
        self.search_max_depth = config.searchMaxDepth

    def _set_mouse_locked(self, x, y, session):
        if self.current_session != session:
            self.current_session = session
            self._update_muted_status(session)

        if self.state == IndicatorState.MOUSE_LOCKED:
            return
        if self.state == IndicatorState.HIDDEN:
            self.indicator.queue_show_indicator(x, y, offset_mode=OffsetMode.CURSOR)
        elif self.state == IndicatorState.WINDOW_LOCKED:
            self.indicator.queue_move_indicator(x, y, offset_mode=OffsetMode.CURSOR)
        self.state = IndicatorState.MOUSE_LOCKED

    def _set_hidden(self):
        self.current_session = None
        if self.state == IndicatorState.HIDDEN:
            return
        self.session_cache.clear()
        self.indicator.queue_hide_indicator()
        self.state = IndicatorState.HIDDEN

    def _update_muted_status(self, session):
        should_appear_muted = check_whether_session_muted(session)
        if self.muted == should_appear_muted:
            return
        self.muted = should_appear_muted
        self.indicator.queue_set_mute(self.muted)

    def _set_window_locked(self, session):
        if self.current_session != session:
            self.current_session = session
            self._update_muted_status(session)

        if self.state == IndicatorState.WINDOW_LOCKED:
            return
        x, y = get_active_window_coordinates()
        if self.state == IndicatorState.HIDDEN:
            self.indicator.queue_show_indicator(x, y, OffsetMode.WINDOW)
        elif self.state == IndicatorState.MOUSE_LOCKED:
            self.indicator.queue_move_indicator(x, y, OffsetMode.WINDOW)
        self.state = IndicatorState.WINDOW_LOCKED

    def _on_activated_scroll(self, x, y, diff):
        pid = get_window_pid_at_location(x, y)
        if not pid:
            return
        session = self._get_session_cached(pid)
        if not session:
            print("no audio session")
        new_volume = adjust_volume_for_session(session, self.volume_scale * diff)
        if new_volume is None:
            return
        self._set_mouse_locked(x, y, session)
        self.indicator.queue_update_indicator(new_volume)

    def _on_increment_key(self):
        pid = get_active_window_pid()
        if not pid:
            return
        session = self._get_session_cached(pid)
        if not session:
            print("no audio session")
        new_volume = adjust_volume_for_session(session, self.key_volume_diff)
        if new_volume is None:
            return
        self._set_window_locked(session)
        self.indicator.queue_update_indicator(new_volume)

    def _on_decrement_key(self):
        pid = get_active_window_pid()
        if not pid:
            return
        session = self._get_session_cached(pid)
        if not session:
            print("no audio session")
        new_volume = adjust_volume_for_session(session, -self.key_volume_diff)
        if new_volume is None:
            return
        self._set_window_locked(session)
        self.indicator.queue_update_indicator(new_volume)

    def _on_release(self):
        self._set_hidden()

    def _on_middle_click(self, x, y):
        pid = get_window_pid_at_location(x, y)
        if not pid:
            return
        session = self._get_session_cached(pid)
        if not session:
            print("no audio session")
        self.muted = toggle_mute(session)
        self.indicator.queue_set_mute(self.muted)
        self._set_mouse_locked(x, y, session)

    def _get_session_cached(self, pid):
        if pid in self.session_cache:
            return self.session_cache[pid]
        session = get_session(
            pid, self.search_children_of_parents, self.search_max_depth
        )
        if session:
            self.session_cache[pid] = session
            return session
        return None

    def _on_cursor_move(self, x, y):
        if self.state == IndicatorState.MOUSE_LOCKED:
            self.indicator.queue_move_indicator(x, y, offset_mode=OffsetMode.CURSOR)

    def _on_mute_key(self):
        pid = get_active_window_pid()
        if not pid:
            return
        session = self._get_session_cached(pid)
        if not session:
            print("no audio session")
        self.muted = toggle_mute(session)
        self._set_window_locked(session)
        self.indicator.queue_set_mute(self.muted)

    def start_event_loop(self):
        """start the event loop, blocks until exit"""
        with use_com_context():
            while True:
                event = self.event_queue.get()
                match event:
                    case ScrollEvent(x, y, magnitude):
                        self._on_activated_scroll(x, y, magnitude)
                    case MiddleMouseEvent(x, y):
                        self._on_middle_click(x, y)
                    case ActivatorReleaseEvent():
                        self._on_release()
                    case CursorMoveEvent(x, y):
                        self._on_cursor_move(x, y)
                    case KeyIncrementEvent():
                        self._on_increment_key()
                    case KeyDecrementEvent():
                        self._on_decrement_key()
                    case KeyMuteToggleEvent():
                        self._on_mute_key()
                    case ExitRequestedEvent():
                        print("exiting")
                        self.end_reason = EventHandlerEndReason.EXIT_REQUESTED
                        self.indicator.queue_close_root()
                        return
                    case RestartRequestedEvent():
                        self.end_reason = EventHandlerEndReason.RESTART_REQUESTED
                        self.indicator.queue_close_root()
                        return
                    case _:
                        print("unknown event")
