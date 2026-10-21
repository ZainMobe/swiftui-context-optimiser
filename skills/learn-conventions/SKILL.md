---
name: learn-conventions
description: Scans an existing SwiftUI codebase and records its conventions (naming, folders, state management, dependency injection, styling, testing) in .claude/conventions.md so new code stays consistent. Use when the developer says "learn conventions", "document our conventions", "how is this project structured", or before the first feature work in an unfamiliar project.
disable-model-invocation: true
allowed-tools: Read, Write, Glob, Grep, Agent, Bash(ls:*), Bash(find:*)
---

Produce `.claude/conventions.md`, at most 40 lines, describing how this project is actually written. Observe; do not prescribe what the code should do.

1. Delegate the survey to a subagent (Explore, or component-finder when only UI patterns are needed) with this brief, so file contents stay out of the main context:
   - Folder layout: top-level groups, whether organised by feature or by type, where views, models, services and resources live. Give one example path each.
   - Naming: view suffixes (`View`, `Screen`, `Page`), view model naming, protocol naming, file-to-type rule, test target naming.
   - State management: `@Observable` vs `ObservableObject`, `@State`/`@Binding` usage, environment injection, any store or redux-like pattern, how views get their dependencies.
   - Navigation: `NavigationStack` with path type, router object, coordinator, sheets handled where.
   - Styling: design tokens or theme file, colour and font access pattern, reusable modifiers, spacing constants.
   - Data: networking layer shape, persistence (SwiftData, Core Data, files), async pattern, error type.
   - Testing: framework (Swift Testing or XCTest), what is covered, naming.
   - Tooling: SwiftLint or swift-format config, localisation approach, preview conventions.
   Ask for counts where patterns are mixed (for example 14 `ObservableObject`, 3 `@Observable`).

2. Write the file
   - Format: `## Section` headers from the list above, one fact per bullet, each with an example path or symbol in backticks. Where patterns are mixed, state the majority pattern and mark it "use this for new code" unless the developer says the minority is the direction of travel; ask once if it is unclear.
   - Do not include anything the component index already lists.

3. Show the file, then write it. Finish with one line stating where it was written and that the session rules will now point new code at it.
