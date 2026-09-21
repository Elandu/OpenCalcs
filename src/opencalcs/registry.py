"""Unified calculation registry assembled from installed plugins."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from opencalcs.plugins import PluginProtocol, discover_plugins


class CalculationRegistry:
    """Collection of calculations exposed by all installed engineering plugins."""

    def __init__(self, plugins: tuple[PluginProtocol, ...] | None = None) -> None:
        self.plugins = plugins if plugins is not None else discover_plugins()
        self._calculations: dict[str, Any] = {}
        for plugin in self.plugins:
            for calculation in plugin.calculations:
                if calculation.id in self._calculations:
                    raise ValueError(f"Duplicate calculation id: {calculation.id}")
                self._calculations[calculation.id] = calculation

    def list_calculations(self) -> list[dict[str, Any]]:
        """Return calculation descriptors in stable identifier order."""

        return [
            self._calculations[calculation_id].descriptor()
            for calculation_id in sorted(self._calculations)
        ]

    def get(self, calculation_id: str) -> Any:
        """Return one calculation by stable identifier."""

        try:
            return self._calculations[calculation_id]
        except KeyError as exc:
            raise KeyError(f"Unknown calculation: {calculation_id}") from exc

    def run(self, calculation_id: str, inputs: Mapping[str, Any]) -> dict[str, Any]:
        """Execute one registered calculation."""

        return self.get(calculation_id).run(inputs)
