## ADDED Requirements

### Requirement: Auto-unlock Trade at Startup

The MCP server SHALL automatically unlock trade during startup if a trade password is provided via environment variable.

#### Scenario: Auto-unlock with plain text password

- **GIVEN** the environment variable `MOOMOO_TRADE_PASSWORD` is set
- **WHEN** the MCP server starts
- **THEN** the server SHALL call `unlock_trade` with the password
- **AND** log a success message indicating REAL account access is enabled

#### Scenario: Auto-unlock with MD5 password

- **GIVEN** the environment variable `MOOMOO_TRADE_PASSWORD_MD5` is set
- **AND** `MOOMOO_TRADE_PASSWORD` is NOT set
- **WHEN** the MCP server starts
- **THEN** the server SHALL call `unlock_trade` with the MD5 password
- **AND** log a success message indicating REAL account access is enabled

#### Scenario: Skip unlock when no password provided

- **GIVEN** neither `MOOMOO_TRADE_PASSWORD` nor `MOOMOO_TRADE_PASSWORD_MD5` is set
- **WHEN** the MCP server starts
- **THEN** the server SHALL skip the unlock step
- **AND** log an info message indicating SIMULATE-only mode

#### Scenario: Handle unlock failure gracefully

- **GIVEN** an environment variable is set with an invalid password
- **WHEN** the MCP server starts
- **THEN** the server SHALL log a warning about the unlock failure
- **AND** continue startup (do not crash)
- **AND** REAL account access will not be available

### Requirement: Manual Unlock Tool

The `unlock_trade` tool SHALL remain available for manual unlocking when auto-unlock is not configured or fails.

#### Scenario: Manual unlock after startup

- **GIVEN** the server started without auto-unlock (no env var set)
- **WHEN** the agent calls `unlock_trade` with a valid password
- **THEN** REAL account access is enabled for the session

### Requirement: Environment Variable Priority

When both `MOOMOO_TRADE_PASSWORD` and `MOOMOO_TRADE_PASSWORD_MD5` are set, the plain text password SHALL take precedence.

#### Scenario: Both env vars set

- **GIVEN** both `MOOMOO_TRADE_PASSWORD` and `MOOMOO_TRADE_PASSWORD_MD5` are set
- **WHEN** the MCP server starts
- **THEN** the server SHALL use `MOOMOO_TRADE_PASSWORD` (plain text)
- **AND** ignore `MOOMOO_TRADE_PASSWORD_MD5`
