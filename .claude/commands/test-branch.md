---
description: "Look at the changes on the branch and identify business logic that needs testing."
allowed-tools: ["Bash", "Read", "Edit", "TodoWrite"]
argument-hint: "[optional: specific patterns to focus on]"
---

- Create a plan listing specific functions that need tests and why, then ask for confirmation before implementing.
- Use the existing testing framework and follow the project's testing conventions.
- Prioritize tests that would catch real bugs over just increasing coverage numbers.
- If 99% of the test is just testing mocked functionality, there's no real value in adding it.
