# /sc:workflow — Instructions

Source: https://github.com/SuperClaude-Org/SuperClaude_Framework/blob/master/SuperClaude/Commands/workflow.md
License: MIT. Derived summary.

## Purpose
Orchestrate multi-step flows (waves, loops, coordination across personas/MCP).

## Inputs
- High-level goal; stages; validation gates

## Outputs
- Executed plan with evidence per stage

## Typical flags
- --wave-mode, --loop, --delegate, --all-mcp | --no-mcp, --validate

## Steps
1) Define stages and quality gates
2) Coordinate personas and server usage
3) Execute per stage; collect evidence
4) Review, iterate, and finalize

## Examples
- `/sc:workflow "migrate project to prod" --wave-mode auto --validate`
