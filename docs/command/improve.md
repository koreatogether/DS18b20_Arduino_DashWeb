# /sc:improve — Instructions

Source: https://github.com/SuperClaude-Org/SuperClaude_Framework/blob/master/SuperClaude/Commands/improve.md
License: MIT. Derived summary.

## Purpose
Iteratively enhance quality (readability, performance, security, docs).

## Inputs
- Target and improvement focus

## Outputs
- Incremental improvements and validation notes

## Typical flags
- --persona-refactorer | --persona-performance | --persona-security, --seq, --validate, --loop

## Steps
1) Identify improvement opportunities and metrics
2) Apply small, safe changes; measure
3) Validate; revert if regression
4) Repeat until goals met

## Examples
- `/sc:improve src/ --focus quality --persona-refactorer --validate --loop`
