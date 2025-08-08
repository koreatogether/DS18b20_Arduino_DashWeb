# /sc:estimate — Instructions

Source: https://github.com/SuperClaude-Org/SuperClaude_Framework/blob/master/SuperClaude/Commands/estimate.md
License: MIT. Derived summary.

## Purpose
Estimate effort, time, and risk for planned work.

## Inputs
- Task list, scope, constraints

## Outputs
- Estimates with assumptions, risks, and buffers

## Typical flags
- --persona-architect | --persona-qa | --persona-performance, --seq

## Steps
1) Break down tasks to small, estimable units
2) Estimate base effort and add risk buffers
3) Identify critical path and dependencies
4) Provide ranges (best/likely/worst) and confidence

## Examples
- `/sc:estimate roadmap/ --persona-architect --seq`
