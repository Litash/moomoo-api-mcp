# OpenD Configuration

## ADDED Requirements

### Requirement: Support Custom Host and Port

The server **MUST** allow configuring the OpenD connection address via environment variables.

#### Scenario: Default Configuration

- Given the environment variables are not set
- When the server starts
- Then it should connect to `127.0.0.1` on port `11111`

#### Scenario: Custom Configuration

- Given `MOOMOO_OPEND_HOST` is set to `192.168.1.100`
- And `MOOMOO_OPEND_PORT` is set to `22222`
- When the server starts
- Then it should connect to `192.168.1.100` on port `22222`
