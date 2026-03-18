---
name: create-compound-component
description: Create, refactor, or review React compound components with practical construction rules. Use when a feature needs composable subcomponents, shared context state, predictable API shape, and consistent accessibility behavior. Prefer Base UI / Radix-style namespace exports such as `Select.Trigger`, `Select.Content`, and `const Select = Object.assign(Root, { ... })` unless the task explicitly preserves a different public API.
---

# Create Compound Component

## Core Principle

Prefer functional correctness, accessibility, and maintainability over stylistic purity.
When reviewing existing code, treat equivalent implementations as valid.
When Base UI primitives already cover the behavior, build on top of them and stay close to their compound-component patterns instead of inventing a parallel abstraction.

## Construction Guidance

1. API shape
- Default to the Base UI / Radix namespace pattern for public API:
  - define the root and leaf parts separately
  - export a single namespace object: `const Component = Object.assign(Root, { Trigger, Content, Item })`
  - prefer consumer usage such as `Component.Trigger` and `Component.Content`
- Keep naming stable across refactors.
- If the repo already exposes a different established API, preserve it unless the task explicitly includes an API migration.
- Avoid alias-only re-export layers unless they add real value.

2. Shared state
- Use context only when parts share state.
- Use `Type | null` context plus `useComponentContext()` guard.
- Throw clear error when parts render outside provider.

3. Structure
- Prefer behavior in component file and styles in `styled.ts`.
- In-file styled primitives are acceptable for small/clear components.
- Do not report “miss” solely because styles are not split.
- When Base UI is already in use, prefer composition over wrapping it into a heavily renamed or reshaped API.

4. Accessibility and semantics
- Preserve semantic elements (`button`, `ul/li`, etc.) and interaction behavior.
- Require ARIA only where widget pattern needs it.
- Do not require `role="option"` if the component is not implementing a full listbox option pattern.

5. Maintainability
- Split when file approaches ~500 LOC or responsibilities blur.
- Prefer composition over boolean-prop proliferation.
- Preserve existing consumer API unless change is requested.
- If Base UI already solves the interaction model, prefer extending its primitives and conventions over rebuilding the behavior from scratch.

6. Verification after changes
- Run `npm run typecheck --workspace @tallyforms/web`.
- Validate keyboard and focus behavior for interactive parts.

## Review Mode Rules

When asked to assess an existing component, report:
- `Pass`: meets intent and no meaningful risk.
- `Acceptable`: style differs from preference but no functional/a11y risk.
- `Issue`: concrete bug, regression risk, or accessibility violation.

Never label a component as failing for:
- using in-file styled primitives,
- using an established local API style,
- missing optional ARIA attributes not required by chosen widget pattern.

Prefer the Base UI / Radix namespace export style for new work and refactors that are already changing the component API surface.

## Minimal Template

```tsx
import React, { createContext, useContext, useState } from 'react';
import {
  ComponentContainer,
  ComponentTriggerButton,
  ComponentContentContainer,
  ComponentItemContainer,
} from './styled';

type ComponentContextValue = {
  isOpen: boolean;
  setIsOpen: React.Dispatch<React.SetStateAction<boolean>>;
  onSelect: (value: string) => void;
};

const ComponentContext = createContext<ComponentContextValue | null>(null);

function useComponentContext() {
  const context = useContext(ComponentContext);

	if (!context) {
	  throw new Error('Component parts must be rendered inside Component');
	}

  return context;
}

function Root({ children, onSelect }: {
  children: React.ReactNode;
  onSelect: (value: string) => void;
}) {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <ComponentContext.Provider value={{ isOpen, setIsOpen, onSelect }}>
      <ComponentContainer>{children}</ComponentContainer>
    </ComponentContext.Provider>
  );
}

function Trigger({ children }: { children: React.ReactNode }) {
  const { isOpen, setIsOpen } = useComponentContext();

  return (
    <ComponentTriggerButton
      type="button"
      aria-expanded={isOpen}
      onClick={() => {
        setIsOpen((previousState) => !previousState);
      }}>
      {children}
    </ComponentTriggerButton>
  );
}

function Content({ children }: { children: React.ReactNode }) {
  const { isOpen } = useComponentContext();

  if (!isOpen) {
    return null;
  }

  return <ComponentContentContainer>{children}</ComponentContentContainer>;
}

function Item({ value, children }: {
  value: string;
  children: React.ReactNode;
}) {
  const { onSelect, setIsOpen } = useComponentContext();

  return (
    <ComponentItemContainer
      onClick={() => {
        onSelect(value);
        setIsOpen(false);
      }}>
      {children}
    </ComponentItemContainer>
  );
}

export const Component = Object.assign(Root, {
  Trigger,
  Content,
  Item,
});
```

## Done Criteria

- Compound parts are explicit and predictable.
- Context guard exists when context is used.
- Accessibility behavior is correct for the chosen widget pattern.
- No unnecessary indirection.
- Typecheck passes after edits.
