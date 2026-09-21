from __future__ import annotations

from dataclasses import dataclass

import pytest

from opencalcs.registry import CalculationRegistry


@dataclass(frozen=True)
class FakeCalculation:
    id: str

    def descriptor(self):
        return {"id": self.id}

    def run(self, inputs):
        return {"value": inputs["value"] * 2}


@dataclass(frozen=True)
class FakePlugin:
    id: str
    name: str
    version: str
    calculations: tuple[FakeCalculation, ...]

    def descriptor(self):
        return {"id": self.id, "name": self.name, "version": self.version}


def test_registry_lists_and_runs_calculations() -> None:
    registry = CalculationRegistry(
        plugins=(FakePlugin("test.plugin", "Test", "1", (FakeCalculation("test.double"),)),)
    )

    assert registry.list_calculations() == [{"id": "test.double"}]
    assert registry.run("test.double", {"value": 3}) == {"value": 6}


def test_registry_rejects_duplicate_ids() -> None:
    calculation = FakeCalculation("test.duplicate")
    with pytest.raises(ValueError, match="Duplicate calculation id"):
        CalculationRegistry(
            plugins=(
                FakePlugin("one", "One", "1", (calculation,)),
                FakePlugin("two", "Two", "1", (calculation,)),
            )
        )
