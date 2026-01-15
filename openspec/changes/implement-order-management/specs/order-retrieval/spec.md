# Order Retrieval

## ADDED Requirements

### Support Getting Order List

The system must allow retrieving a list of orders (today's orders) filtered by environment and account.

#### Scenario: Get Today's Orders

Given the user wants to see their orders
When they call `get_orders(trd_env='REAL')`
Then the tool should return a list of orders including order ID, code, side, price, qty, status.

### Support Getting Deal List

The system must allow retrieving a list of executed deals.

#### Scenario: Get Today's Deals

Given the user wants to see their executions
When they call `get_deals(trd_env='REAL')`
Then the tool should return a list of deals including deal ID, order ID, code, price, qty.
