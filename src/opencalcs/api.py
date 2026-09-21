"""OpenCalcs host API."""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict

from opencalcs import __version__
from opencalcs.registry import CalculationRegistry


class CalculationRunRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    inputs: dict[str, Any]


def create_app(registry: CalculationRegistry | None = None) -> FastAPI:
    """Create the OpenCalcs API with an optional explicit registry for testing."""

    runtime = registry or CalculationRegistry()
    app = FastAPI(title="OpenCalcs", version=__version__)

    def calculation_descriptor(calculation_id: str) -> dict[str, Any]:
        definition = runtime.get(calculation_id)
        descriptor = definition.descriptor()
        for plugin in runtime.plugins:
            if any(item.id == calculation_id for item in plugin.calculations):
                descriptor["plugin"] = {
                    "id": plugin.id,
                    "name": plugin.name,
                    "version": plugin.version,
                }
                break
        return descriptor

    @app.get("/health/live")
    def health_live() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/api/v1/plugins")
    @app.get("/api/plugins")
    def plugins() -> list[dict[str, Any]]:
        return [plugin.descriptor() for plugin in runtime.plugins]

    @app.get("/api/v1/calculations")
    @app.get("/api/calculations")
    def calculations() -> list[dict[str, Any]]:
        return [
            calculation_descriptor(definition["id"])
            for definition in runtime.list_calculations()
        ]

    @app.get("/api/v1/calculations/{calculation_id}")
    @app.get("/api/calculations/{calculation_id}")
    def calculation(calculation_id: str) -> dict[str, Any]:
        try:
            return calculation_descriptor(calculation_id)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @app.post("/api/v1/calculations/{calculation_id}/run")
    @app.post("/api/calculations/{calculation_id}/run")
    def run_calculation(
        calculation_id: str,
        request: CalculationRunRequest,
    ) -> dict[str, Any]:
        try:
            return runtime.run(calculation_id, request.inputs)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

    return app


app = create_app()
