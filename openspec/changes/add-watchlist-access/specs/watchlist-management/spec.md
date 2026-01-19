# Spec: Watchlist Management

## ADDED Requirements

### R1: List Security Groups

The system MUST provide a tool to list all user-defined security groups.

#### Scenario: User lists groups

- **Given** the user has custom groups "Favorites" and "Tech"
- **When** the `get_user_security_group` tool is called
- **Then** it returns a list of groups, including their IDs and names

### R2: List Group Securities

The system MUST provide a tool to list all securities within a specific security group.

#### Scenario: User gets stocks in "Favorites"

- **Given** the user has a group "Favorites" containing "US.AAPL" and "US.NVDA"
- **When** the `get_user_security` tool is called with the group name "Favorites"
- **Then** it returns a list of securities in that group, each with their code and name
