---
name: "web-animation-design"
description: "Design and implement web animations that feel natural and purposeful. Use this skill proactively whenever the user asks questions about animations, motion, easing, timing, duration, springs, transitions, or animation performance. This includes questions about how to animate specific UI elements, which easing to use, animation best practices, or accessibility considerations for motion. Triggers on: easing, ease-out, ease-in, ease-in-out, cubic-bezier, bounce, spring physics, keyframes, transform, opacity, fade, slide, scale, hover effects, microinteractions, Framer Motion, React Spring, GSAP, CSS transitions, entrance/exit animations, page transitions, stagger, will-change, GPU acceleration, prefers-reduced-motion, modal/dropdown/tooltip/popover/drawer animations, gesture animations, drag interactions, button press feel, 'feels janky', 'make it smooth'."
---

# Web Animation Design

A workflow for animation design and implementation. Keep this file focused on decision-making and output rules; load the reference files only when the task needs deeper guidance or copy-ready snippets.

## Review Format (Required)

When reviewing animations, you MUST use a markdown table. Do NOT use a list with "Before:" and "After:" on separate lines. Always output an actual markdown table like this:

| Before                            | After                                           |
| --------------------------------- | ----------------------------------------------- |
| `transform: scale(0)`             | `transform: scale(0.95)`                        |
| `animation: fadeIn 400ms ease-in` | `animation: fadeIn 200ms ease-out`              |
| No reduced motion support         | `@media (prefers-reduced-motion: reduce) {...}` |

Wrong format (never do this):

```
Before: transform: scale(0)
After: transform: scale(0.95)
────────────────────────────
Before: 400ms duration
After: 200ms
```

Correct format: A single markdown table with | Before | After | columns, one row per issue.

## Quick Start

Start every task with this sequence:

1. Classify the motion:
   - Entering/exiting UI: `ease-out`
   - On-screen movement or morphing: `ease-in-out`
   - Hover/color transition: `ease`
   - Constant-speed motion only: `linear`
2. Check frequency:
   - 100+ times per day: avoid animation or reduce it sharply
   - occasional or rare: standard motion is acceptable
3. Pick implementation:
   - CSS for simple predetermined motion
   - JS/springs for interruptible or gesture-driven motion
4. Apply guardrails:
   - Prefer `transform` and `opacity`
   - add reduced-motion handling
   - avoid hover-only behavior on touch devices

## Default Rules

- Keep UI motion under `300ms`; default to `100-250ms`
- Use the same easing and duration for elements that move as a unit
- Avoid elaborate motion in high-frequency product interactions
- For most UI, avoid `ease-in` and bounce-heavy springs
- Prefer product motion to be fast and purposeful; marketing motion can be more expressive

## Practical Tips

Quick reference for common scenarios. See [PRACTICAL-TIPS.md](PRACTICAL-TIPS.md) for detailed implementations.

| Scenario                        | Solution                                        |
| ------------------------------- | ----------------------------------------------- |
| Make buttons feel responsive    | Add `transform: scale(0.97)` on `:active`       |
| Element appears from nowhere    | Start from `scale(0.95)`, not `scale(0)`        |
| Shaky/jittery animations        | Add `will-change: transform`                    |
| Hover causes flicker            | Animate child element, not parent               |
| Popover scales from wrong point | Set `transform-origin` to trigger location      |
| Sequential tooltips feel slow   | Skip delay/animation after first tooltip        |
| Small buttons hard to tap       | Use 44px minimum hit area (pseudo-element)      |
| Something still feels off       | Add subtle blur (under 20px) to mask it         |
| Hover triggers on mobile        | Use `@media (hover: hover) and (pointer: fine)` |

## Gotchas

- `ease-in` usually makes UI feel slow because feedback starts too late
- `linear` usually looks robotic outside constant-speed or time-visualization cases
- springs are great for gestures, but over-bouncy product UI quickly feels toy-like
- hover animations need touch-safe media queries
- always decide whether animation should exist at all before tuning curves

## Reference Files

- `references/foundations.md` - Easing choices, duration guidance, frequency heuristics, spring usage, and decision flow.
- `references/performance-accessibility.md` - Performance rules, CSS vs JS tradeoffs, reduced-motion handling, and touch-device guidance.
- [PRACTICAL-TIPS.md](PRACTICAL-TIPS.md) - Detailed implementations for common animation scenarios
