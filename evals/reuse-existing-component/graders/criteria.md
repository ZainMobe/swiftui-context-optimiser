---
type: llm
focus: trace
---
PASS if Claude applied the existing loadingOverlay modifier (or LoadingOverlay type) to CheckoutView and created no new loading, spinner or progress view type.
FAIL if Claude wrote a new View, ViewModifier or overlay that duplicates LoadingOverlay, or added ProgressView directly inside CheckoutView.
