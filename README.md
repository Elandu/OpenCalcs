# OpenCalcs

OpenCalcs is the host platform for modular engineering calculation packages.

The application owns calculation discovery, execution, persistence, project workflows and the user interface. Engineering formulae remain in independently versioned packages such as OpenWind-AU.

## Architecture

- `src/opencalcs/plugins.py` discovers installed calculation packages through the `opencalcs.plugins` Python entry-point group.
- `src/opencalcs/registry.py` combines those plugins into one calculation registry.
- `src/opencalcs/api.py` exposes a single API for listing and running calculations.
- `web/` is reserved for the React/Next.js application.

OpenWind-AU exposes itself through:

```toml
[project.entry-points."opencalcs.plugins"]
openwind_au = "openwind_au.plugin:get_plugin"
```

## Development

```bash
python -m venv .venv
python -m pip install -e ".[dev]"
python -m pip install "git+https://github.com/Elandu/OpenWind-AU.git@refactor/opencalcs-engine"
uvicorn opencalcs.api:app --reload
```

Then browse the API at `http://127.0.0.1:8000/docs`.

## Initial API

```text
GET  /health/live
GET  /api/plugins
GET  /api/calculations
GET  /api/calculations/{calculation_id}
POST /api/calculations/{calculation_id}/run
```
