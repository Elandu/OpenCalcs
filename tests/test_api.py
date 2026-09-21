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

    expected = [
        {
            "id": "test.double",
            "name": "Double",
            "plugin": {"id": "test.plugin", "name": "Test", "version": "1"},
        }
    ]
    assert client.get("/api/calculations").json() == expected
    assert client.get("/api/v1/calculations").json() == expected

    response = client.post("/api/calculations/test.double/run", json={"inputs": {"value": 4}})
    versioned_response = client.post(
        "/api/v1/calculations/test.double/run",
        json={"inputs": {"value": 4}},
    )
    assert response.status_code == 200
    assert versioned_response.status_code == 200
    assert response.json() == {"value": 8}
    assert versioned_response.json() == {"value": 8}
