# Benchmark: plugin on vs off

Four implementation tasks on PhotoBooth, a production iOS app with 446 Swift files and a 396-entry component index. Each task ran once with the plugin on and once with it off, on separate throwaway copies of the source. Nothing was compiled.

- Plugin on: a Haiku 5.5 component-finder agent runs first (3 to 5 tool calls), then a Sonnet 5.5 implementer receives the rule block, the component index path and the finder verdict.
- Plugin off: the same Sonnet 5.5 implementer with the task prompt only.

![Summary](benchmark-summary-linkedin.png)

## Results

| | Plugin on | Plugin off | Change |
|---|---|---|---|
| Tasks that reused or extended an existing component | 4 of 4 | 1 of 4 (plus 1 partial) | |
| Cost, cache-normalised official API prices | $0.185 | $0.206 | -10% |
| Cost, as billed in this run | $0.583 | $0.610 | -4% |
| Output tokens written by the implementer | 1,418 | 2,035 | -30% |
| API requests to Sonnet | 18 | 21 | -14% |
| API requests to Haiku (finder) | 17 | 0 | |
| Lines added | 76 | 95 | -20% |

![Cost per task](benchmark-cost-per-task.png)

![Output tokens and lines added](benchmark-output-and-lines.png)

![Component reuse](benchmark-reuse.png)

## What each run produced

| Task | Plugin on | Plugin off |
|---|---|---|
| Gallery loading skeleton | Extended the existing GallerySkeletonView with a columnCount parameter so it matches the real grid. One source of truth kept. | Bypassed GallerySkeletonView and inlined a LazyVGrid of GalleryMediaCellSkeleton tiles, leaving GallerySkeletonView orphaned. |
| Support screen tooltip | Reused the existing TooltipView for the bubble; built only the icon button inline. | Wrote a new inline bubble (Text + background + offset), a duplicate of TooltipView. |
| Exit PIN before leaving gallery | Reused ExitPinDialogView, the exact-fit component that was sitting unused. | Reused PinEntryDialogView in verify mode, copying the title and 6-digit subtitle from AttractView. |
| Share dialog reset countdown | Extended Video360TimeoutCountdownBadge with a label closure and reused it (default keeps old call sites unchanged). Pill styling may be heavy for a dialog. | Built an inline Text countdown. Clean and arguably closer to 'small text', but a third countdown label in the codebase. |

## Method and caveats

1. Token figures come from the per-request `usage` fields in each agent transcript. Costs use the official per-million-token prices for Sonnet 5.5 and Haiku 5.5 (Haiku priced per request by prompt length).
2. "Cache-normalised" treats the shared system-prompt prefix as a cache read on every request, so the result does not depend on which agent happened to warm the cache first. "As billed" is what the run actually cost in this harness.
3. The harness used for the runs carries a fixed prefix of about 76k tokens (system prompt plus tool schemas) in every request; a no-tool probe measured it at 76,534 tokens for Sonnet and 76,528 for Haiku. It is identical on both sides.
4. One run per cell. Agent runs vary, so treat the percentages as indicative, not stable.
5. The plugin's comment blocker and read guards were active in the harness for both sides, so they do not separate the two columns. The difference measured here is the rule block, the component index and the finder agent.
6. Nothing was compiled; each agent listed the assumptions it could not check.
7. The gallery skeleton task turned out to be partly done already (GalleryView already showed GallerySkeletonView). The plugin run noticed and extended it; the plain run replaced it with an inline grid.

Raw data: `results.json` and `results.csv` in this folder.
