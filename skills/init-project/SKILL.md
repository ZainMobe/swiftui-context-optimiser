---
name: init-project
description: Sets up a SwiftUI project for low-token Claude Code sessions. Use when the developer says "init project", "set up this project for the optimiser", "scaffold CLAUDE.md", or starts work in a Swift project that has no CLAUDE.md or component index.
disable-model-invocation: true
argument-hint: "[--no-explore-override]"
allowed-tools: Read, Write, Edit, Glob, Grep, Bash(python3:*), Bash(ls:*), Bash(mkdir:*), Bash(cp:*), Bash(xcodebuild:*), Bash(swift:*), Bash(cat:*)
---

Scaffold the project for token-efficient sessions. Make no change without showing the developer what will be written. Ask one question at a time and only when the answer cannot be read from the project.

1. Detect the project
   - Glob for `*.xcodeproj`, `*.xcworkspace`, `Package.swift`. If none, say this is not a Swift project and stop.
   - Read the deployment target and Swift version from the project file or `Package.swift` with Grep (`IPHONEOS_DEPLOYMENT_TARGET`, `SWIFT_VERSION`, `swift-tools-version`, `platforms:`). Do not read whole pbxproj files.
   - Detect the package manager (SPM `Package.resolved`, `Podfile`, `Cartfile`).
   - Derive build and test commands: for an Xcode project use `xcodebuild -scheme <scheme> -destination 'generic/platform=iOS Simulator' build`; list schemes with `xcodebuild -list -json` if needed. For SPM use `swift build` / `swift test`.

2. Build the component index
   - Run `python3 "${CLAUDE_PLUGIN_ROOT}/hooks/scripts/reindex.py" "<project-root>"` and report the entry count in one line.

3. CLAUDE.md
   - If `CLAUDE.md` does not exist: fill `${CLAUDE_PLUGIN_ROOT}/templates/CLAUDE.md.template`, replacing every `{{PLACEHOLDER}}` with detected values. For `{{ARCHITECTURE_NOTE}}` and `{{DECISION}}`, ask the developer for one line each or remove the bullet if they skip. Show the result, then write it.
   - If `CLAUDE.md` exists: Read it. Propose the minimal edit that adds the "Working rules" and "Compact instructions" sections and removes lines that duplicate them. Target under 80 lines total. Show the diff before editing.

4. Path-scoped Swift rule
   - Create `.claude/rules/` if missing and copy `${CLAUDE_PLUGIN_ROOT}/templates/swift-rules.md` to `.claude/rules/swift.md`. Skip if a file with equivalent content already exists.

5. Conventions
   - If `.claude/conventions.md` is missing and the project already has at least 10 Swift files, suggest running `/swiftui-context-optimiser:learn-conventions` next. Do not run it automatically.

6. Haiku Explore override (skip if `--no-explore-override` was passed)
   - Check whether `~/.claude/agents/Explore.md` exists. If it does not, ask the developer once whether to install the low-cost Explore agent from `${CLAUDE_PLUGIN_ROOT}/templates/Explore.md`. It applies to all their projects, so say so. Copy it only on a yes.

7. Git hygiene
   - If the project is a git repository, ask whether `.claude/swiftui-components.md` should be added to `.gitignore` (it is regenerated locally; committing it creates merge noise). Apply on a yes.

8. Finish with a four-line summary: files created or changed, index entry count, the next command to run, and nothing else.
