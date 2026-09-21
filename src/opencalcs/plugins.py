"""Discovery of installed engineering calculation plugins."""

from __future__ import annotations

from importlib.metadata import entry_points
from typing import Any, Protocol


class PluginProtocol(Protocol):
    id: str
    name: str
    version: str
    calculations: tuple[Any, ...]

    def descriptor(self) -> dict[str, Any]: ...


def discover_plugins() -> tuple[PluginProtocol, ...]:
    """Load installed packages registered in the OpenCalcs plugin group."""

    discovered: list[PluginProtocol] = []
    for entry_point in entry_points(group="opencalcs.plugins"):
        factory = entry_point.load()
        plugin = factory()
        discovered.append(plugin)
    return tuple(sorted(discovered, key=lambda plugin: plugin.id))
