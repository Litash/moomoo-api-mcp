# Order Modification and Cancellation

## ADDED Requirements

### Support Modifying Orders

The system must allow modifying price, quantity, or other attributes of an open order.

#### Scenario: Modify Order Price

Given an open order with ID '12345'
When a user calls `modify_order(order_id='12345', op='NORMAL', price=355.0)`
Then the order modification request should be sent to Moomoo
And the tool should return success status.

### Support Cancelling Orders

The system must allow cancelling an open order.

#### Scenario: Cancel Order

Given an open order with ID '67890'
When a user calls `cancel_order(order_id='67890')`
Then the order cancellation request (MODIFY with CANCEL op) should be sent to Moomoo
And the tool should return success status.
