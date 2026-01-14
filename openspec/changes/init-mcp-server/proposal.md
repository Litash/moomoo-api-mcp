# Init MCP Server

## Background

We need to establish the foundation for the Moomoo MCP server to allow AI agents to interact with the Moomoo trading platform. This involves setting up the project structure, dependencies, and a basic health check capability to verify connectivity with the OpenD gateway.

## Goal

Initialize the `moomoo-api-mcp` project with a FastMCP server, configure dependencies using `uv`, and implement a "system health" tool to check the connection status with the Moomoo API (OpenD).

## Key Changes

- Initialize Python project with `uv` and `pyproject.toml`.
- Create source directory structure `src/moomoo_mcp`.
- Implement `server.py` using `mcp.server.fastmcp`.
- Implement `startup` and `shutdown` lifecycle management for Moomoo connection.
- Add `check_health` tool to verify OpenD connectivity.
