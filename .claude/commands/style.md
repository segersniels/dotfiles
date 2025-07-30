---
description: "Analyze the current PR's code changes and suggest coding style and readability improvements."
allowed-tools: ["Bash", "Read", "Edit", "TodoWrite"]
argument-hint: "[optional: specific patterns to focus on]"
---

# Instructions

1. Identify all changed files of the current PR
2. Review each modified file for coding style and readability issues, focusing on:
   - **Naming conventions**: Variables, functions, classes should have clear, descriptive names
   - **Code structure**: Proper indentation, spacing, and organization
   - **Function/method length**: Identify overly long functions that should be broken down
   - **Code complexity**: Spot nested conditionals, long parameter lists, or complex expressions
   - **Comments and documentation**: Missing or unclear comments, outdated documentation
   - **Consistency**: Inconsistent formatting, naming patterns, or code patterns within the codebase
   - **Dead code**: Unused variables, imports, or commented-out code blocks
   - **Magic numbers/strings**: Hard-coded values that should be constants
   - **Error handling**: Missing or inadequate error handling patterns

3. For each issue identified, provide:
   - **Location**: File path and line number(s)
   - **Issue description**: Clear explanation of the problem
   - **Suggested improvement**: Specific recommendation with example code if helpful
   - **Impact level**: Low/Medium/High based on readability improvement potential

4. Prioritize suggestions by impact:
   - **High**: Issues that significantly impact code readability or maintainability
   - **Medium**: Improvements that enhance code clarity
   - **Low**: Minor style inconsistencies or optional improvements

5. Group suggestions by category (naming, structure, documentation, etc.) for easier review.

6. Provide a summary with:
   - Total number of files reviewed
   - Number of suggestions by priority level
   - Most common types of issues found

7. When requested by the user to fix the issues — be sure to make atomic commits for every individual issue that was fixed.

# Tools

- Use `gh` to fetch the current PR's information
- Use language-specific linters or formatters when available
- Consider the existing codebase patterns and conventions