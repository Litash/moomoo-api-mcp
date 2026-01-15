# Order Placement

## ADDED Requirements

### Support placing orders

The system must allow placing orders with `code`, `side`, `qty`, `price`, `order_type`, and `trd_env`.
Supported order types include: `NORMAL` (Limit), `MARKET`, `STOP`, `STOP_LIMIT`, `TRAILING_STOP`, `TRAILING_STOP_LIMIT`, `AUCTION`, `AUCTION_LIMIT`, etc.

#### Scenario: Place Limit Buy Order

Given the user wants to buy 100 shares of HK.00700 at 350.0
When they call `place_order(code='HK.00700', side='BUY', qty=100, price=350.0, order_type='NORMAL')`
Then the order should be submitted to Moomoo
And the tool should return the order ID.

#### Scenario: Place Market Buy Order

Given the user wants to buy 100 shares of US.AAPL at market price
When they call `place_order(code='US.AAPL', side='BUY', qty=100, price=0.0, order_type='MARKET')`
Then the order should be submitted
And the tool should return the order ID.
