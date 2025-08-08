# /sc:test — Instructions

Source: https://github.com/SuperClaude-Org/SuperClaude_Framework/blob/master/SuperClaude/Commands/test.md
License: MIT. Derived summary.

## Purpose
Execute tests, generate reports, and improve coverage/quality gates.

## Inputs
- Test type: unit | integration | e2e | security | performance

## Outputs
- Test logs, coverage, failure triage

## Typical flags
- --persona-qa, --play (E2E), --seq, --validate, --coverage

## Steps
1) Select scope and type; collect fixtures
2) Run tests; capture logs/metrics
3) Analyze failures; create follow-ups
4) Update coverage; gate on thresholds

## Examples
- `/sc:test --type security --play --persona-qa`
