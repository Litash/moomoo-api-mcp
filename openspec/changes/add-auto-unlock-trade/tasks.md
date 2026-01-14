# Tasks: Add Auto-unlock Trade at Startup

## 1. Implementation

- [x] 1.1 Add environment variable reading for `MOOMOO_TRADE_PASSWORD` and `MOOMOO_TRADE_PASSWORD_MD5` in `server.py`
- [x] 1.2 Add auto-unlock logic to `app_lifespan` after `trade_service.connect()`
- [x] 1.3 Add logging to indicate unlock status at startup (success/skipped/failed)
- [x] 1.4 Update README with environment variable configuration section

## 2. Testing

- [x] 2.1 Add unit test for auto-unlock when env var is set
- [x] 2.2 Add unit test for graceful skip when env var is not set
- [x] 2.3 Verify existing tests still pass
