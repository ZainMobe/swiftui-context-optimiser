---
name: usage-report
description: Reports where this project's most recent Claude Code session spent context (tool calls, largest tool results, files read repeatedly) and recommends concrete reductions. Use when the developer says "usage report", "where did my tokens go", "why is this session expensive", or "token breakdown".
disable-model-invocation: true
allowed-tools: Bash(python3:*), Read
---

Explain where context was spent and what to change, using measured data rather than impressions.

1. Run `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/usage_report.py" "<project-root>"` and read its output. If it reports no transcript, say so and stop.

2. Interpret, in at most 12 lines
   - Name the top three consumers by result size and what they were (for example "Read of pbxproj, 48k chars").
   - For each, give the specific cheaper alternative: Grep with a pattern, Read with offset and limit, the Explore or component-finder subagent, the build filter, or `/clear` between unrelated tasks.
   - If any file was read more than twice, call it out and suggest a line-range read or a rule in CLAUDE.md to avoid it.
   - If tool results exceed roughly 60 percent of the transcript, recommend running `/compact` with a focus string or `/clear` now.

3. Do not print the raw script output back; the developer can run it. Do not pad with general advice that the data does not support.
