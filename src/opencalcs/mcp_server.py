"""Model Context Protocol server for the OpenCalcs calculation registry."""

from __future__ import annotations

import argparse
import os
from collections.abc import Sequence
from typing import Any

from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings

from opencalcs import __version__
from opencalcs.registry import CalculationRegistry

MCP_TRANSPORTS = ("stdio", "streamable-http")
runtime = CalculationRegistry()

mcp = FastMCP(
    "OpenCalcs",
    instructions=(
        "Discover and execute versioned engineering calculations exposed by installed "
        "OpenCalcs plugins. Calculation outputs must be treated as engineering calculation "
        "records and reviewed by an appropriately qualified engineer where required."
    ),
    stateless_http=True,
    json_response=True,
)
mcp._mcp_server.version = __version__


def _descriptor(calculation_id: str) -> dict[str, Any]:
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


@mcp.tool()
def list_plugins() -> list[dict[str, Any]]:
    """List installed engineering calculation plugins and their versions."""

    return [plugin.descriptor() for plugin in runtime.plugins]


@mcp.tool()
def list_calculations(
    plugin_id: str | None = None,
    category: str | None = None,
) -> list[dict[str, Any]]:
    """List calculations available through OpenCalcs, optionally filtered."""

    calculations = [_descriptor(item["id"]) for item in runtime.list_calculations()]
    if plugin_id is not None:
        calculations = [
            item for item in calculations if item.get("plugin", {}).get("id") == plugin_id
        ]
    if category is not None:
        calculations = [
            item
            for item in calculations
            if str(item.get("category", "")).casefold() == category.casefold()
        ]
    return calculations


@mcp.tool()
def describe_calculation(calculation_id: str) -> dict[str, Any]:
    """Return schema, standard references, version and plugin provenance."""

    return _descriptor(calculation_id)


@mcp.tool()
def run_calculation(
    calculation_id: str,
    inputs: dict[str, Any],
) -> dict[str, Any]:
    """Execute one registered calculation by its stable OpenCalcs identifier."""

    definition = _descriptor(calculation_id)
    result = runtime.run(calculation_id, inputs)
    return {
        "calculation": definition,
        "inputs": inputs,
        "result": result,
    }


def main(argv: Sequence[str] | None = None) -> int:
    """Run the OpenCalcs MCP server over stdio or Streamable HTTP."""

    parser = argparse.ArgumentParser(
        prog="opencalcs-mcp",
        description="Run the OpenCalcs MCP calculation registry.",
    )
    parser.add_argument(
        "--transport",
        choices=MCP_TRANSPORTS,
        default=os.environ.get("OPENCALCS_MCP_TRANSPORT", "stdio"),
    )
    parser.add_argument(
        "--host",
        default=os.environ.get("OPENCALCS_MCP_HOST", "127.0.0.1"),
    )
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.environ.get("OPENCALCS_MCP_PORT", "8001")),
    )
    args = parser.parse_args(argv)

    mcp.settings.host = args.host
    mcp.settings.port = args.port

    if args.transport == "streamable-http":
        allowed_hosts = [
            item.strip()
            for item in os.environ.get("OPENCALCS_MCP_ALLOWED_HOSTS", "").split(",")
            if item.strip()
        ]
        allowed_origins = [
            item.strip()
            for item in os.environ.get("OPENCALCS_MCP_ALLOWED_ORIGINS", "").split(",")
            if item.strip()
        ]
        if args.host in {"0.0.0.0", "::"} and not allowed_hosts:
            parser.error(
                "OPENCALCS_MCP_ALLOWED_HOSTS is required for wildcard HTTP binds."
            )
        if args.host not in {"0.0.0.0", "::"} and args.host not in allowed_hosts:
            allowed_hosts.append(args.host)
        mcp.settings.transport_security = TransportSecuritySettings(
            enable_dns_rebinding_protection=True,
            allowed_hosts=allowed_hosts,
            allowed_origins=allowed_origins,
        )

    mcp.run(transport=args.transport)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
