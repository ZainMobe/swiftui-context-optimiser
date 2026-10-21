---
paths:
  - "**/*.swift"
---
- Before declaring a new View, ViewModifier, *Style, Shape or View extension, confirm it is absent from .claude/swiftui-components.md.
- One type per file, file named after the type, placed in the feature folder the conventions file specifies.
- No comments, doc comments or `// MARK:` lines unless asked.
- Match the project's state management style (see .claude/conventions.md); do not introduce a second pattern.
- Do not add third-party packages without asking.
- Prefer editing an existing file over creating a new one when extending behaviour.
