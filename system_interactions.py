"""system interactions"""

from typing import Optional, Set
from dataclasses import dataclass

import ctypes
from contextlib import contextmanager
import psutil
import win32api
import win32gui
import win32process
from pycaw.pycaw import AudioUtilities
from pynput.keyboard import KeyCode


@dataclass
class SearchResult:
    """Stores data while performing search for audio sessions"""

    active_pid: Optional[int]
    first_inactive_pid: Optional[int]
    inactive_pid_depth: int
    finished_child_searches: Set[int]


def find_top_explorer():
    """We want to exclude the top level explorer pid from the search,
    or we'll traverse the tree to unrelated apps..."""
    for proc in psutil.process_iter(["name", "pid", "ppid"]):
        try:
            if proc.info["name"].lower() != "explorer.exe":
                continue
            highest_pid = None
            while proc and proc.info["name"].lower() == "explorer.exe":
                highest_pid = proc.info["pid"]
                proc = proc.parent()
            return highest_pid
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return None


explorer_pid = find_top_explorer()


def get_window_pid_at_location(x, y):
    """Returns the PID of the window at the given location"""
    hwnd = win32gui.WindowFromPoint((x, y))
    if hwnd:
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        return pid
    return None


def adjust_volume_for_session(session, diff):
    """Adjusts the volume of the given session by the given diff"""
    if not session:
        return None

    volume = session.SimpleAudioVolume
    current_volume = volume.GetMasterVolume()
    new_volume = max(0.0, min(current_volume + diff, 1.0))
    volume.SetMasterVolume(new_volume, None)
    return new_volume


def check_whether_session_muted(session):
    """returns true if the given session is muted"""
    volume_data = session.SimpleAudioVolume
    muted = volume_data.GetMute()
    return muted


def toggle_mute(session):
    """Toggles the mute state of the given session"""
    if not session:
        return None
    volume = session.SimpleAudioVolume
    muted = volume.GetMute()
    volume.SetMute(not muted, None)
    return not muted


def get_active_window_pid():
    """Returns the PID of the active window"""
    hwnd = win32gui.GetForegroundWindow()
    return win32process.GetWindowThreadProcessId(hwnd)[1]


def get_session(pid, search_children_of_parents, max_depth):
    """Returns the audio session for the given PID"""
    inactive_sessions_for_pids = dict()
    active_sessions_for_pids = dict()
    for session in AudioUtilities.GetAllSessions():
        if session.Process:
            if session.State == 1:
                active_sessions_for_pids[session.Process.pid] = session
            elif session.State == 0:
                inactive_sessions_for_pids[session.Process.pid] = session
    inactive_session_pids = set(inactive_sessions_for_pids.keys())
    active_session_pids = set(active_sessions_for_pids.keys())

    search_results = find_related_pid_with_audio(
        pid,
        active_session_pids,
        inactive_session_pids,
        max_depth,
        search_children_of_parents,
    )
    active_session_pid = search_results.active_pid
    if active_session_pid:
        return active_sessions_for_pids[active_session_pid]
    inactive_session_pid = search_results.first_inactive_pid
    if inactive_session_pid:
        return inactive_sessions_for_pids[inactive_session_pid]
    return None


def get_window_coordinates(hwnd):
    """Returns the x, y coordinates of the given window"""
    return win32gui.GetWindowRect(hwnd)[:2]


def get_active_window_coordinates():
    """Returns the x, y coordinates of the active window"""
    return get_window_coordinates(win32gui.GetForegroundWindow())


def get_session_for_specific_pid(pid):
    """Returns the audio session for the given PID"""
    sessions = AudioUtilities.GetAllSessions()
    for session in sessions:
        if session.Process and session.Process.pid == pid:
            return session
    return None


def find_related_pid_with_audio(
    prospect_pid,
    active_session_pids,
    inactive_session_pids,
    max_depth,
    search_children_of_parents,
) -> SearchResult:
    """Finds the first pid with active audio - or, closest pid with inactive audio"""

    # passed through search mechanism by reference
    search_results = SearchResult(
        active_pid=None,
        first_inactive_pid=None,
        inactive_pid_depth=100,
        finished_child_searches=set(),
    )

    if prospect_pid in active_session_pids:
        search_results.active_pid = prospect_pid
        return search_results
    if prospect_pid in inactive_session_pids:
        search_results.first_inactive_pid = prospect_pid
        search_results.inactive_pid_depth = 0

    # 4: system
    # what else do we want here?
    exclusions = (4, explorer_pid)

    if prospect_pid in exclusions:
        return search_results

    find_related_pid_with_audio_descending(
        prospect_pid,
        active_session_pids,
        inactive_session_pids,
        0,
        max_depth,
        search_results,
    )
    if search_results.active_pid:
        return search_results
    find_related_pid_with_audio_both_directions(
        prospect_pid,
        active_session_pids,
        inactive_session_pids,
        exclusions,
        max_depth,
        search_children_of_parents,
        search_results,
    )
    return search_results


def find_related_pid_with_audio_both_directions(
    prospect_pid,
    active_session_pids,
    inactive_session_pids,
    exclusions,
    max_depth,
    search_children_of_parents,
    search_results,
):
    """Finds the first pid with active audio - or, closest pid with inactive audio"""
    if prospect_pid in active_session_pids:
        search_results.active_pid = prospect_pid
        return

    if prospect_pid in exclusions:
        return

    i = 0
    try:
        process = psutil.Process(prospect_pid)
        while process and i < max_depth:
            if process.pid in active_session_pids:
                search_results.active_pid = process.pid
                return
            if (
                process.pid in inactive_session_pids
                and not search_results.inactive_pid
                or i < search_results.inactive_pid_depth
            ):
                search_results.inactive_pid = process.pid
                search_results.inactive_pid_depth = i
            if search_children_of_parents:
                find_related_pid_with_audio_descending(
                    process.pid,
                    active_session_pids,
                    inactive_session_pids,
                    0,
                    max_depth,
                    search_results,
                )
                if search_results.active_pid:
                    return
                search_results.finished_child_searches.add(process.pid)
            process = process.parent()
            i += 1
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        pass


def find_related_pid_with_audio_descending(
    target_pid,
    active_reference_pids,
    inactive_reference_pids,
    current_depth,
    max_depth,
    search_results,
):
    """Finds the first pid with active audio - or, closest pid with inactive audio"""

    if (target_pid) in search_results.finished_child_searches:
        return

    if target_pid in active_reference_pids:
        search_results.active_pid = target_pid
        return
    if target_pid in inactive_reference_pids and (
        search_results.inactive_pid_depth is None
        or current_depth < search_results.inactive_pid_depth
    ):
        search_results.inactive_pid_depth = current_depth
        search_results.inactive_pid = target_pid
        return

    try:
        children = psutil.Process(target_pid).children()
        for child in children:
            if child.pid in active_reference_pids:
                search_results.active_pid = child.pid
                return
            if (
                target_pid in inactive_reference_pids
                and search_results.inactive_pid_depth is None
                or current_depth < search_results.inactive_pid_depth
            ):
                search_results.inactive_pid_depth = current_depth
                search_results.inactive_pid = target_pid
            if (
                child.pid not in search_results.finished_child_searches
                and current_depth < max_depth
            ):
                find_related_pid_with_audio_descending(
                    child.pid,
                    active_reference_pids,
                    inactive_reference_pids,
                    current_depth + 1,
                    max_depth,
                    search_results,
                )
                if search_results.active_pid:
                    return
                search_results.finished_child_searches.add(child.pid)
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        pass


@contextmanager
def use_com_context():
    """context manager for using the com context"""
    ctypes.windll.ole32.CoInitialize(None)
    try:
        yield
    finally:
        ctypes.windll.ole32.CoUninitialize()


def char_to_vk(char):
    """Converts a character to a Virtual Key Code"""
    return win32api.VkKeyScan(char)


def get_keycode_from_char(char):
    """Converts a character to a KeyCode object"""
    vk = win32api.VkKeyScan(char)
    if vk == -1:
        return None
    kc = KeyCode.from_vk(vk & 0xFF)
    kc.char = char
    return kc


def print_session_name(session):
    """Prints the name of the given audio session"""
    if session and session.Process:
        print(f"Session name: {session.Process.name()}")
    elif session:
        print("Session name: System Sounds")
    else:
        print("No valid session provided")
