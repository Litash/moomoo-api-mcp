# Enhanced Order Types Support

## ADDED Requirements

### Requirement: Support All Order Types

The system SHALL support all Moomoo API order types.

#### Scenario: User places a specialized order

- When the user calls `place_order` with `order_type='SPECIAL_LIMIT'` and `time_in_force='DAY'`.
- Then the system should call the API with `OrderType.SPECIAL_LIMIT`.

### Requirement: Validate Order Type Support

The tool documentation and implementation SHALL validate the list of supported order types.

#### Scenario: Tool description exposes order types

- The `moomoo_place_order` tool description explicitly lists all supported order types (e.g., MARKET, NORMAL, STOP, etc.) so that the AI Agent is aware of them.
