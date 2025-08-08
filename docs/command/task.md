# /sc:task — Instructions

Source: https://github.com/SuperClaude-Org/SuperClaude_Framework/blob/master/SuperClaude/Commands/task.md
License: MIT. Derived summary.

## Purpose
Create, track, and complete structured tasks with clear acceptance criteria.

## Inputs
- Title, description, scope, done-definition

## Outputs
- Task plan, checklist, and result summary

## Typical flags
- --persona-architect|qa, --validate, --seq

## Steps
1) Define outcome and acceptance criteria
2) Break into checklist; order by dependencies
3) Execute with evidence collection
4) Mark done when criteria met and validated

## Examples
- `/sc:task "cppcheck fix" --persona-qa --validate`
