# Change: Add Auto-unlock Trade at Startup

## Why

AI agents need REAL account access to be useful for live trading workflows. Currently, agents must call `unlock_trade` with a password, but they have no secure way to obtain this password. This creates a poor UX where the agent either fails on REAL account queries or repeatedly asks the user for credentials.

## What Changes

- Read `MOOMOO_TRADE_PASSWORD` or `MOOMOO_TRADE_PASSWORD_MD5` from environment variables
- Auto-unlock trade during `app_lifespan` if the env var is set
- Log a clear message indicating unlock status at startup
- Update README with environment variable configuration
- Keep `unlock_trade` tool for manual unlocking (e.g., if env var not set)

## Impact

- Affected specs: New `trade-unlock` capability
- Affected code:
  - `src/moomoo_mcp/server.py` - Add unlock logic to `app_lifespan`
  - `README.md` - Add environment variable documentation
