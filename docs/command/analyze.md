# /sc:analyze — Instructions

Source: https://github.com/SuperClaude-Org/SuperClaude_Framework/blob/master/SuperClaude/Commands/analyze.md
License: MIT (SuperClaude Framework). This is a derived summary; refer to the upstream doc for canonical details.

## Purpose
Analyze codebases, systems, or artifacts to produce findings and recommendations.

## Inputs
- Target path or scope (file/dir/pattern)
- Optional focus: performance | security | quality | architecture

## Outputs
- Findings report (issues, risks, patterns)
- Recommended actions and next steps

## Prerequisites
- Read access to repo/files
- Optional: MCP servers enabled for docs/test/security as needed

## Typical flags
- Personas: --persona-analyzer, --persona-security, --persona-performance
- Thinking: --think | --think-hard | --ultrathink
- MCP: --seq (analysis), --c7 (docs), --no-mcp (disable)
- Safety/validation: --safe-mode, --validate

## Steps
1) Scope: identify target directory/files and focus.
2) Context build: read key files, dependency manifests, configs.
3) Analyze: architecture, risks, complexity, smell patterns.
4) Validate: reproduce issues where possible; gather evidence.
5) Report: summarize findings + prioritized actions.

## Examples
- Comprehensive: `/sc:analyze repo/ --persona-analyzer --think-hard --seq --validate`
- Security-focused: `/sc:analyze api/ --focus security --persona-security --seq`
