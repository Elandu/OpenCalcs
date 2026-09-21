from __future__ import annotations

from dataclasses import dataclass

import opencalcs.mcp_server as mcp_server
from opencalcs.registry import CalculationRegistry


@dataclass(frozen=True)
class FakeCalculation:
    id: str = "test.double"

    def descriptor(self):
        return {
            "id": self.id,
            "name": "Double",
            "category": "test",
            "input_schema": {"type": "object"},
        }

    def run(self, inputs):
        return {"value": inputs["value"] * 2}


@dataclass(frozen=True)
class FakePlugin:
    id: str = "test.plugin"
    name: str = "Test"
    version: str = "1"
    calculations: tuple = (FakeCalculation(),)

    def descriptor(self):
        return {
            "id": self.id,
            "name": self.name,
            "version": self.version,
            "calculations": [item.descriptor() for item in self.calculations],
        }


def test_mcp_catalog_and_execution_use_shared_registry(monkeypatch) -> None:
    registry = CalculationRegistry(plugins=(FakePlugin(),))
    monkeypatch.setattr(mcp_server, "runtime", registry)

    calculations = mcp_server.list_calculations()
    assert calculations == [
        {
            "id": "test.double",
            "name": "Double",
            "category": "test",
            "input_schema": {"type": "object"},
            "plugin": {"id": "test.plugin", "name": "Test", "version": "1"},
        }
    ]

    result = mcp_server.run_calculation("test.double", {"value": 5})
    assert result["calculation"]["plugin"]["id"] == "test.plugin"
    assert result["result"] == {"value": 10}
