# /sc:spawn — Instructions

Source: https://github.com/SuperClaude-Org/SuperClaude_Framework/blob/master/SuperClaude/Commands/spawn.md
License: MIT. Derived summary.

## Purpose
Create sub-tasks or delegate to specialized agents/personas.

## Inputs
- Parent goal, sub-task definitions

## Outputs
- Assigned sub-tasks and coordination plan

## Typical flags
- --delegate, --persona-*, --seq, --no-mcp (if isolation)

## Steps
1) Decompose goal into independent sub-tasks
2) Assign appropriate persona/server per task
3) Define interfaces/sync points; avoid conflicts
4) Aggregate results and validate integration

## Examples
- `/sc:spawn "dash + firmware" --delegate auto --seq`
