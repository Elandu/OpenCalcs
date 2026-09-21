from __future__ import annotations

from dataclasses import dataclass

from fastapi.testclient import TestClient

from opencalcs.api import create_app
from opencalcs.registry import CalculationRegistry


@dataclass(frozen=True)
class FakeCalculation:
    id: str = "test.double"

    def descriptor(self):
        return {"id": self.id, "name": "Double"}

    def run(self, inputs):
        return {"value": inputs["value"] * 2}


@dataclass(frozen=True)
class FakePlugin:
    id: str = "test.plugin"
    name: str = "Test"
    version: str = "1"
    calculations: tuple = (FakeCalculation(),)

    def descriptor(self):
        return {"id": self.id, "name": self.name, "version": self.version}


def test_api_lists_and_runs_calculation() -> None:
    app = create_app(CalculationRegistry(plugins=(FakePlugin(),)))
    client = TestClient(app)

    assert client.get("/api/calculations").json() == [{"id": "test.double", "name": "Double"}]
    response = client.post("/api/calculations/test.double/run", json={"inputs": {"value": 4}})
    assert response.status_code == 200
    assert response.json() == {"value": 8}
