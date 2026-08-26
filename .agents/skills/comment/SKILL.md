---
name: comment
description: "Add, remove, or move code comments in requested code. Write new or revised comments with ASD-STE100 Simplified Technical English principles. Use when the user asks for comments, better comments, comment placement, why-comments, JSDoc, or comments that make code easier to review."
---

# Comment

Add, remove, or move comments using the original Human Code comment guidance.

## Comments

- Comments should help a reviewer scan the code and understand the product-level flow without fully diving into the implementation.
- Prefer high-level product intent over low-level mechanics.
- Comment why a guard exits or why a branch exists.
- Put comments that explain an `if` branch directly above the `if`; for `if`/`else`, put branch-specific comments inside the relevant block.
- Use `//` for single-line comments.
- Use JSDoc for multi-line comments or function explanations.

## Simplified Technical English

- Write each new or revised prose comment with ASD-STE100 Simplified Technical English principles.
- Preserve the exact spelling of code identifiers, API names, literals, and established domain terms. Treat them as technical terms.
- Use American English and one term for one meaning. Do not vary a term only for style.
- Write complete, active-voice sentences. Give one subject or idea in each sentence. Use no more than 25 words in each sentence.
- Use simple words, explicit subjects, and unambiguous pronouns. Repeat the noun when a pronoun can refer to more than one item.
- Do not use contractions. Avoid `-ing` verb forms when a clear finite verb gives the same meaning.
- Do not claim formal ASD-STE100 compliance unless the text was checked against the official rules and controlled dictionary.
