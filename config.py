"""Loads config.yaml and returns a Config object"""

from typing import NamedTuple
from yaml import safe_load
from keycode_serde import string_to_keycodes
from system_interactions import char_to_vk
import os
import sys


class Config(NamedTuple):
    """Available settings"""

    activatorHotkey: list
    incrementKey: int
    decrementKey: int
    muteToggleKey: int
    exitKey: int
    indicatorSize: int
    indicatorXCursorOffset: int
    indicatorYCursorOffset: int
    indicatorXWindowOffset: int
    indicatorYWindowOffset: int
    indicatorColor: str
    scrollVolumeScale: float
    keyVolumeScale: float
    searchChildrenOfParents: bool
    searchMaxDepth: int


def _get_config_path():
    if getattr(sys, "frozen", False):
        base_path = os.path.dirname(sys._MEIPASS)
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, "config.yaml")


def load_config():
    """Loads config.yaml and returns a Config object"""
    with open(_get_config_path(), "r", encoding="utf-8") as f:
        raw_config = safe_load(f)
        config = Config(
            activatorHotkey=string_to_keycodes(
                raw_config.get("activatorHotkey", "ctrl+shift")
            ),
            incrementKey=char_to_vk(raw_config.get("incrementKey", "}")),
            decrementKey=char_to_vk(raw_config.get("decrementKey", "{")),
            muteToggleKey=char_to_vk(raw_config.get("muteToggleKey", "M")),
            exitKey=char_to_vk(raw_config.get("exitKey", "X")),
            indicatorSize=raw_config.get("indicatorSize", 80),
            indicatorColor=raw_config.get("indicatorColor", "green"),
            indicatorXWindowOffset=raw_config.get("indicatorXWindowOffset", 80),
            indicatorYWindowOffset=raw_config.get("indicatorYWindowOffset", 80),
            indicatorXCursorOffset=raw_config.get("indicatorXCursorOffset", 15),
            indicatorYCursorOffset=raw_config.get("indicatorYCursorOffset", 15),
            scrollVolumeScale=raw_config.get("scrollVolumeScale", 0.1),
            keyVolumeScale=raw_config.get("keyVolumeScale", 0.1),
            searchChildrenOfParents=raw_config.get("searchChildrenOfParents", False),
            searchMaxDepth=raw_config.get("searchMaxDepth", 2),
        )
        return config
