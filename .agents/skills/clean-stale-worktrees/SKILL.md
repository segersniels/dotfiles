---
name: clean-stale-worktrees
description: Detect and safely remove stale linked Git worktrees and their disk contents. Use when the user wants to audit, prune, or clean up old worktrees, including large ignored directories such as node_modules.
---

# Clean Stale Worktrees

Use the bundled scripts. Do not reconstruct the checks in shell.

Requires Git, Python 3.9+, and `lsof` on macOS or Linux.

## Available scripts

- `scripts/detect_stale_worktrees.py` inspects linked worktrees and writes a JSON manifest.
- `scripts/clean_stale_worktrees.py` reads that manifest, revalidates its candidates, and removes safe worktrees with `git worktree remove`.

`git worktree remove` deletes the registered worktree directory, including ignored content such as `node_modules`. The cleanup script does not delete branches.

## Workflow

1. Create the manifest outside any candidate worktree:

   ```bash
   manifest=$(mktemp)
   python3 scripts/detect_stale_worktrees.py --repo "$REPOSITORY" --days 3 --output "$manifest"
   ```

2. Read the JSON manifest. Explain each candidate and relevant skip reason. `unused` means all of these are true:

   - No process has a current working directory inside the tree.
   - No worktree file or per-worktree Git metadata changed within the threshold.
   - Tracked and untracked files are clean. Ignored files may remain.
   - The worktree is unlocked.
   - `HEAD` is reachable from a local branch, remote-tracking branch, or tag.

3. Clean only when the user asked for removal, not merely detection or an audit:

   ```bash
   python3 scripts/clean_stale_worktrees.py "$manifest" --confirm REMOVE
   ```

4. Report removed paths, newly skipped paths, and failures. Do not claim cleanup for a failed removal.

An explicit request such as “clean up stale worktrees” authorizes removal of candidates that pass these checks. A request to inspect, detect, list, or audit does not.

## Guardrails

- Never remove the main worktree, a locked worktree, a dirty worktree, an active worktree, a recently modified worktree, or an unreferenced detached `HEAD`.
- Cleanup must consider only candidates recorded in the supplied manifest and must revalidate them immediately before removal.
- Never delete a directory directly, delete a branch, or run `git worktree prune`.
- Never pass `--force`. Ordinary `git worktree remove` removes ignored build and dependency content from an otherwise clean tree.
- Fail closed when `lsof`, filesystem inspection, manifest validation, or Git checks fail.
- Do not install a scheduler, background job, hook, or launch agent unless the user separately asks for recurring automation.

Run either script with `--help` for its complete interface and exit codes.
