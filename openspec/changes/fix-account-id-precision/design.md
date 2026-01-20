## Context

The Moomoo API uses 64-bit integers for Account IDs. JSON standard (RFC 8259) does not enforce precision limits on numbers, but most implementations (JavaScript, Python's `json` with default settings interacting with JS clients) treat numbers as double-precision floats, which lose precision beyond safe integer limits (2^53 - 1).

## Goals / Non-Goals

- **Goals**: Ensure Account IDs are transmitted without precision loss between the MCP client (LLM/User) and the MCP server.
- **Non-Goals**: Change the underlying Moomoo SDK types (which expect `int`). We will convert at the boundary.

## Decisions

- **Decision**: Change `acc_id` type in MCP tool signatures from `int` to `str`. Tools strictly enforce `str` type to prevent precision loss.
- **Rationale**: Strings are the standard solution for handling 64-bit integers in JSON-based protocols to avoid precision loss.

## Risks / Trade-offs

- **Risk**: Existing clients sending `int` might break if we strictly enforce `str`.
- **Mitigation**: We will allow `int | str` in the signature but document and encourage `str`. The internal logic will convert `str` to `int` before calling the SDK, as Python `int` has arbitrary precision and can handle the 64-bit value if it was received correctly (which is the problem for `int` input from JSON, but if a client sends it as a valid number that Python parses correctly, fine. But usually the _client_ has already rounded it before sending. So we MUST tell the client to send `str`).

## Migration Plan

- No data migration needed.
- Tool definition update is immediate.
