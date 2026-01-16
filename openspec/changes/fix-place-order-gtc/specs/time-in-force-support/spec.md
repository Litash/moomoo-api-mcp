# Time in Force Support

## ADDED Requirements

### Requirement: Support Time in Force Parameter

The system SHALL support specifying a Time in Force (e.g., GTC, DAY) when placing an order.

#### Scenario: User places a GTC order

- When the user calls `place_order` with `time_in_force='GTC'`.
- Then the system should pass `TimeInForce.GTC` (or equivalent) to the underlying Moomoo API.
- And the order verification message should display "GTC" for Time in Force.

#### Scenario: User places a DAY order

- When the user calls `place_order` with `time_in_force='DAY'`.
- Then the system should pass `TimeInForce.DAY` (or equivalent) to the underlying Moomoo API.

#### Scenario: User does not specify time_in_force

- When the user calls `place_order` without `time_in_force`.
- Then the system should default to `DAY`.
- And the order verification message should reflect the default.
