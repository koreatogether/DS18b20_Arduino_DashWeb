# /sc:git — Instructions

Source: https://github.com/SuperClaude-Org/SuperClaude_Framework/blob/master/SuperClaude/Commands/git.md
License: MIT. Derived summary.

## Purpose
Assist with Git operations: branching, commits, PR hygiene, history analysis.

## Inputs
- Repo path; operation (branch/commit/rebase/PR)

## Outputs
- Git commands, suggested messages, safety checks

## Typical flags
- --persona-devops | --persona-scribe, --validate, --safe-mode

## Steps
1) Identify goal and safe sequence (no history loss)
2) Prepare commands; draft conventional commits
3) Validate status/diff; run secret scans if needed
4) Execute and confirm remote state

## Examples
- `/sc:git prepare-release --persona-devops --validate`
