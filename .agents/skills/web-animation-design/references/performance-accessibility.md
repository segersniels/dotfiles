# Performance And Accessibility

## Performance Golden Rule

Prefer animating `transform` and `opacity`.

Avoid animating:

- `padding`, `margin`, `height`, `width`
- heavy `blur` values, especially in Safari
- deep CSS-variable-driven animations when they force broad style recalculation

## Optimization Techniques

```css
.animated-element {
  will-change: transform;
}
```

Use `will-change` selectively, not everywhere.

React-specific guidance:

- keep frame-by-frame updates outside React render when possible
- use refs for transient style updates
- avoid state changes on every frame

## CSS vs JavaScript

Choose CSS when motion is simple and predetermined.

- often smoother under load
- lower implementation overhead
- good for enter/exit, hover, and straightforward keyframes

Choose JS when motion is dynamic or interruptible.

- gesture-driven interactions
- springs
- coordinated stateful choreography

Framer Motion note:

```jsx
<motion.div animate={{ transform: "translateX(100px)" }} />
<motion.div animate={{ x: 100 }} />
```

Prefer patterns that preserve GPU-friendly transforms in the output your stack generates.

## Reduced Motion

Whenever you add motion, provide a reduced-motion path.

```css
.modal {
  animation: fadeIn 200ms ease-out;
}

@media (prefers-reduced-motion: reduce) {
  .modal {
    animation: none;
  }
}
```

Guidelines:

- every animated element should have a reduced-motion behavior
- `animation: none` or `transition: none` is usually sufficient
- do not assume opacity/color motion is always acceptable
- autoplay media should become click-to-play

Framer Motion example:

```jsx
import { useReducedMotion } from "framer-motion";

function Component() {
  const shouldReduceMotion = useReducedMotion();

  return (
    <motion.div
      initial={shouldReduceMotion ? false : { opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
    />
  );
}
```

## Touch Devices

Guard hover-only effects so they do not fire on touch.

```css
@media (hover: hover) and (pointer: fine) {
  .element:hover {
    transform: scale(1.05);
  }
}
```

Touch devices can trigger hover on tap, so this guard prevents sticky or misleading states.
