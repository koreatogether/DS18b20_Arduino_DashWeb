# /sc:implement — Instructions

Source: https://github.com/SuperClaude-Org/SuperClaude_Framework/blob/master/SuperClaude/Commands/implement.md
License: MIT. Derived summary.

## Purpose
Implement a planned feature/spec into working code.

## Inputs
- Spec/issue, target module, acceptance criteria

## Outputs
- Code changes, tests, and brief changelog

## Typical flags
- --persona-backend|frontend, --seq, --validate, --safe-mode

## Steps
1) Confirm requirements; identify interfaces
2) Implement incrementally with tests
3) Run build/tests/static checks
4) Summarize changes and impacts

## Examples
- `/sc:implement feature:sensor-calibration --seq --validate`
