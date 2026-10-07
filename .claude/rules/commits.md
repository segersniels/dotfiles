# Commits

Each commit holds one change that a reviewer can read and revert on its own. When a rule here conflicts with the repository's own conventions, follow the repository.

## Before you commit

- Commit only when the user asks. A request to commit does not authorize a push.
- Run `git status` and read the diffs. If files are already staged, commit only those files. Do not add more.
- Leave unrelated changes untouched, staged or not.
- Stage explicit paths or hunks. Inspect `git diff --cached` before each commit.
- Complete the repository's required checks and evaluate warnings.
- Do not skip hooks with `--no-verify`. If a hook fails, fix the cause and commit again.

## Boundaries

- Give each commit one reason to revert. Split dependencies, tooling or config, refactors, docs, and each feature or fix into separate commits.
- Keep a manifest and its lockfile in the same commit.
- Keep tests in the same commit as the behavior they prove.
- Keep changes together when a split would leave a commit broken or misleading.

## Messages

- Read `git log --oneline -10` and match the repository's scopes and tone.
- Use Conventional Commits: `type(scope): description`. Write the title in lowercase imperative mood, under 100 characters, and describe the outcome.
- For dependencies, use `chore(deps): add|update|remove <package> [to <version>]`. Use `chore(deps-dev)` for development dependencies.
- Prefer a title-only commit. Add a body only to explain why: a rationale, a migration note, or a non-obvious constraint. Keep body lines under 100 characters.
- Pass the title and each body paragraph with a separate `-m` flag. Use single quotes so the shell does not expand backticks or `$`. Do not use heredocs or `cat`, and do not include ANSI codes.
