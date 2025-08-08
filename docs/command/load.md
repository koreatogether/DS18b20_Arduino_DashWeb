# /sc:load — Instructions

Source: https://github.com/SuperClaude-Org/SuperClaude_Framework/blob/master/SuperClaude/Commands/load.md
License: MIT. Derived summary.

## Purpose
Load context: files, specs, datasets, or project metadata for analysis.

## Inputs
- Paths/globs; context size limits; filters

## Outputs
- Context snapshot and summary index

## Typical flags
- --uc (compression), --seq, --c7

## Steps
1) Select relevant files with globs and size filters
2) Extract summaries/metadata; avoid noise
3) Store/return context index for downstream steps

## Examples
- `/sc:load src/ include/ --uc`
