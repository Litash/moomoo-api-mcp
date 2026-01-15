# Spec: Account Tools Simplification

## ADDED Requirements

### Requirement: Remove Account Indexing

The system MUST NOT expose `acc_index` as a parameter in account tools, ensuring agents identify accounts explicitly by `acc_id`.

#### Scenario: Agent requests assets

Given an agent needing account assets
When calling `get_assets`
Then the tool accepts `acc_id`
And the tool does NOT accept `acc_index`

### Requirement: Unified Account Summary

The system MUST provide a high-level tool that aggregates assets and positions into a single response.

#### Scenario: Get full account state

Given an authenticated user
When `get_account_summary` is called with `acc_id`
Then return a structure containing both `assets` and `positions`
