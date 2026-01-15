# Spec: Market K-Line

## ADDED Requirements

### Requirement: Retrieve Historical K-Lines

The system MUST provide a tool `get_historical_kline` that returns historical candlestick data.

#### Scenario: User requests daily candles for analysis

- **Given** the agent is analyzing "US.TSLA" price acton over the last week
- **When** the `get_historical_kline` tool is called with `code="US.TSLA"`, `ktype="K_DAY"`
- **Then** the system returns a list of daily candles with date, open, high, low, close, and volume.

### Requirement: Retrieve Real-time/Recent K-Lines

The system MUST allow retrieving the most recent K-lines for intraday analysis.

#### Scenario: User requests 1-minute candles

- **Given** the agent needs intraday data
- **When** the `get_historical_kline` tool is called with `ktype="K_1M"`
- **Then** the system returns 1-minute granularity candles.
