# Motion Foundations

## Easing Blueprint

### `ease-out`

Use for user-initiated interactions and enter/exit motion: dropdowns, modals, tooltips, popovers.

```css
/* Sorted weak to strong */
--ease-out-quad: cubic-bezier(0.25, 0.46, 0.45, 0.94);
--ease-out-cubic: cubic-bezier(0.215, 0.61, 0.355, 1);
--ease-out-quart: cubic-bezier(0.165, 0.84, 0.44, 1);
--ease-out-quint: cubic-bezier(0.23, 1, 0.32, 1);
--ease-out-expo: cubic-bezier(0.19, 1, 0.22, 1);
--ease-out-circ: cubic-bezier(0.075, 0.82, 0.165, 1);
```

Why it works: strong initial acceleration creates quick feedback, then the element settles.

### `ease-in-out`

Use when elements already on screen move or morph.

```css
/* Sorted weak to strong */
--ease-in-out-quad: cubic-bezier(0.455, 0.03, 0.515, 0.955);
--ease-in-out-cubic: cubic-bezier(0.645, 0.045, 0.355, 1);
--ease-in-out-quart: cubic-bezier(0.77, 0, 0.175, 1);
--ease-in-out-quint: cubic-bezier(0.86, 0, 0.07, 1);
--ease-in-out-expo: cubic-bezier(1, 0, 0, 1);
--ease-in-out-circ: cubic-bezier(0.785, 0.135, 0.15, 0.86);
```

### `ease`

Use for hover states and color transitions.

```css
transition: background-color 150ms ease;
```

### `linear`

Only for constant-speed motion or time visualization.

- marquees
- tickers
- hold-to-delete progress indicators

### `ease-in`

Usually avoid in UI. It delays feedback and makes interfaces feel sluggish.

## Paired Elements Rule

Elements that animate together should use the same easing and duration.

```css
.modal {
  transition: transform 200ms ease-out;
}

.overlay {
  transition: opacity 200ms ease-out;
}
```

## Duration Guidelines

| Element Type                      | Duration  |
| --------------------------------- | --------- |
| Micro-interactions                | 100-150ms |
| Standard UI (tooltips, dropdowns) | 150-250ms |
| Modals, drawers                   | 200-300ms |

Rules:

- Keep product UI motion under `300ms`
- Larger elements can move slightly slower than smaller ones
- Exit motion can be about 20% faster than entrance
- Longer distance can justify slightly longer duration

## Frequency Heuristic

- `100+` times per day: usually remove or heavily reduce motion
- occasional use: standard motion is fine
- rare or first-time interactions: more expressive motion can work

## When to Animate

Do animate:

- enter/exit transitions for spatial continuity
- state changes that benefit from visual continuity
- responses to direct user actions
- rare interactions where delight adds value

Do not animate:

- keyboard-initiated interactions
- hover effects on very frequent controls
- anything used constantly where speed matters more than delight

Marketing vs product:

- marketing pages can tolerate longer, more expressive motion
- product UI should stay fast, purposeful, and restrained

## Springs

Use springs for:

- drag interactions
- interruptible gestures
- playful or organic interfaces
- elements that should preserve momentum

Recommended mental model:

```js
{ type: "spring", duration: 0.5, bounce: 0.2 }
```

Traditional physics form:

```js
{ type: "spring", mass: 1, stiffness: 100, damping: 10 }
```

Bounce guidance:

- default to little or no bounce
- use subtle bounce (`0.1-0.3`) for playful or gesture-based interactions
- avoid bounce-heavy motion in dense product UI

## Decision Flow

Is the element entering or exiting?
-> `ease-out`

Else, is it moving or morphing on screen?
-> `ease-in-out`

Else, is it a hover or color transition?
-> `ease`

Else, is it constant-speed motion?
-> `linear`

Else:
-> default to `ease-out`
