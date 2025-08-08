# /sc:build — Instructions

Source: https://github.com/SuperClaude-Org/SuperClaude_Framework/blob/master/SuperClaude/Commands/build.md
License: MIT (SuperClaude Framework). Derived summary; see upstream for canonical details.

## Purpose
Build or assemble artifacts/features from a plan or spec.

## Inputs
- Target module or path
- Build type: feature | component | service | docs site

## Outputs
- New/updated files and a short build log

## Prerequisites
- Clear requirements or spec
- Toolchain readiness (package managers, compilers)

## Typical flags
- Personas: --persona-frontend | --persona-backend | --persona-architect
- MCP: --magic (UI), --seq (analysis), --c7 (docs lookup)
- Safety: --safe-mode, --validate

## Steps
1) Confirm requirements/scope; list dependencies
2) Create/update files; follow repo conventions
3) Validate build; run quick self-checks
4) Summarize outputs and next steps

## Examples
- UI: `/sc:build ui/button/ --persona-frontend --magic --c7`
- Backend: `/sc:build api/session/ --persona-backend --seq --validate`
