# /sc:cleanup — Instructions

Source: https://github.com/SuperClaude-Org/SuperClaude_Framework/blob/master/SuperClaude/Commands/cleanup.md
License: MIT. Derived summary.

## Purpose
Reduce technical debt: remove dead code, simplify, standardize.

## Inputs
- Scope: path(s) or module(s)
- Targets: unused code, warnings, duplication

## Outputs
- Cleaned files; changelog of refactors/removals

## Typical flags
- --persona-refactorer, --think, --seq, --validate

## Steps
1) Discover: list dead/duplicate/problematic areas
2) Plan: safe order of changes; add suppressions if needed
3) Execute: small, reversible commits; maintain behavior
4) Validate: build/tests/static analysis

## Examples
- `/sc:cleanup src/ --persona-refactorer --seq --validate`
