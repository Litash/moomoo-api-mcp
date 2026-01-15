# system-health Specification

## Purpose
TBD - created by archiving change init-mcp-server. Update Purpose after archive.
## Requirements
### Requirement: Check Server Health

The system MUST provide a tool to check the health and connectivity of the MCP server and its downstream OpenD gateway.

#### Scenario: Verify connectivity to OpenD

Given the OpenD gateway is running and accessible
When the user invokes `check_health`
Then the system returns a status of "connected"
And includes version information of the connected OpenD gateway (if available).

#### Scenario: Report connection failure

Given the OpenD gateway is NOT running or accessible
When the user invokes `check_health`
Then the system returns a status of "disconnected"
And includes an error message describing the connection issue.

