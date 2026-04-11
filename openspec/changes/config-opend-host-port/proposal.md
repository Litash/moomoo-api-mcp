# Configurable OpenD Host and Port

## Context
Currently, the MCP server hardcodes the Moomoo OpenD connection to `127.0.0.1:11111`. Users running OpenD on a different machine or port cannot connect without code modification.

## Problem
Users cannot configure the OpenD address, limiting deployment flexibility (e.g., running MCP in a container separate from OpenD).

## Solution
Introduce `MOOMOO_OPEND_HOST` and `MOOMOO_OPEND_PORT` environment variables to configure the connection address.

## Scope
- Modify `server.py` to read these environment variables.
- Pass the values to `MoomooService` and `TradeService`.
- Default to `127.0.0.1` and `11111` to maintain backward compatibility.
