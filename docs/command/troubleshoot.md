# /sc:troubleshoot — Instructions

Source: https://github.com/SuperClaude-Org/SuperClaude_Framework/blob/master/SuperClaude/Commands/troubleshoot.md
License: MIT. Derived summary.

## Purpose
Systematically investigate and resolve problems.

## Inputs
- Error logs, repro steps, environment info

## Outputs
- Root cause analysis, fix, and validation

## Typical flags
- --persona-analyzer, --think, --seq, --validate, --introspect

## Steps
1) Reproduce; isolate minimal failing case
2) Form hypotheses; collect evidence
3) Fix with smallest viable change
4) Validate and add regression tests

## Examples
- `/sc:troubleshoot "serial COM4 timeout" --persona-analyzer --seq --validate`
