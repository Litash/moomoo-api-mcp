## MODIFIED Requirements

### Requirement: Get Account List

The system SHALL provide a tool to retrieve the list of trading accounts available to the user.

#### Scenario: Get Account List

Given the agent needs to know available accounts
When the `get_accounts` tool is called
Then it should return a list of trading accounts with their IDs (as strings to preserve precision), types, and simulation status

### Requirement: Get Account Assets

The system SHALL provide a tool to retrieve the asset summary (cash, market value) for a specific account.

#### Scenario: Get Assets

Given the user has funds in their account
When the `get_assets` tool is called with an account ID (as string)
Then it should return the total assets, cash, market value, and purchasing power

### Requirement: Get Account Positions

The system SHALL provide a tool to retrieve the current positions held in a trading account.

#### Scenario: Get Positions

Given the user holds stocks
When the `get_positions` tool is called with an account ID (as string)
Then it should return a list of held securities with stock code, quantity, cost price, and current market value

#### Scenario: Get Positions by Market

Given the user holds stocks in multiple markets (e.g. US, HK)
When the `get_positions` tool is called with a specific `market` (e.g. "US") and account ID (as string)
Then it should return only the positions for that market

### Requirement: Get Max Tradable Quantity

The system SHALL provide a tool to calculate the maximum tradable quantity for a security.

#### Scenario: Get Max Buy

Given the user wants to buy a stock
When the `get_max_tradable` tool is called with code, price, and account ID (as string)
Then it should return the maximum number of shares they can buy based on available funds

### Requirement: Get Cash Flow

The system SHALL provide a tool to retrieve the cash flow history of the account.

#### Scenario: Get Cash History

Given the user wants to see transaction history
When the `get_cash_flow` tool is called with a date range and account ID (as string)
Then it should return a list of cash transactions (deposits, withdrawals, fees)
