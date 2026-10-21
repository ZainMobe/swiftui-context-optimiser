---
name: digest
description: Consolidates a project's CLAUDE.md and Claude Code auto-memory into one lean digest and removes stale, duplicated or derivable notes. Use when the developer says "digest memory", "clean up notes", "compact the project memory", or when the session start context reports a memory digest is due.
disable-model-invocation: true
allowed-tools: Read, Write, Edit, Glob, Grep, Bash(ls:*), Bash(wc:*), Bash(python3:*), Bash(git:*)
---

Reduce the project's persistent notes to what future sessions need, and nothing a future session can re-derive from the code in a few seconds.

1. Locate the sources
   - Project `CLAUDE.md`, `CLAUDE.local.md`, `.claude/rules/*.md`, `.claude/conventions.md`.
   - Auto-memory directory: `~/.claude/projects/<slug>/memory/` where `<slug>` is the project path with every non-alphanumeric character replaced by `-`. Read `MEMORY.md` and every topic file it links.
   - Report sizes in lines before changing anything.

2. Classify every line into one bucket
   - KEEP: decisions with reasons, conventions, non-obvious gotchas, external constraints (API limits, App Store review notes), build or test commands, open questions for the developer.
   - MERGE: the same fact stated in two places, or several lines that collapse into one.
   - DROP: completed task logs, step-by-step narration, facts derivable from the code (file lists, type names, what a function does), anything about a file or feature that no longer exists (verify with Glob or Grep before dropping), time-bound status ("currently working on").

3. Propose the digest
   - Rewrite CLAUDE.md to under 60 lines using the section order: project line, Working rules, Build and test, Architecture, Decisions, Compact instructions.
   - Rewrite MEMORY.md as an index of at most 40 lines; keep topic files only when a topic has more than 10 lines of KEEP content, otherwise inline it.
   - Show the developer: lines before and after per file, the DROP list in full (one line each), and the MERGE pairs. Wait for approval. Never delete a file without an explicit yes for that file.

4. Apply
   - Write the approved versions. If the project is under git and CLAUDE.md changed, mention that it is uncommitted; do not commit.

5. Finish with two lines: total lines removed, and the date to run the next digest (suggest four weeks or when the session start nudge reappears).

Rules for the digest text itself: imperative, one fact per line, no headers deeper than `##`, no examples unless the rule is ambiguous without one, no restating anything the plugin's session rules already inject.
