---
name: clean-stale-worktrees
description: Detect and safely remove stale linked Git worktrees and their disk contents. Use when the user wants to audit, prune, or clean up old worktrees, including large ignored directories such as node_modules.
---

# Clean Stale Worktrees

Use the bundled detector and cleaner for Git and process checks. Judge whether the work is complete from the worktree's purpose and PR or thread state, not age alone.

Requires Git, Python 3.9+, `lsof` on macOS or Linux, and an authenticated GitHub CLI (`gh`).

## Decide what is eligible

- Identify review worktrees from their path, branch name, PR number, and associated thread. A PR authored by someone else is supporting evidence that the checkout was used for review, not proof on its own.
- A completed review or a merged or closed PR can qualify immediately. Use the three-day inactivity threshold as a fallback when completion is unclear.
- A settled T3 thread does not need to be archived. Check for ongoing work; an unarchived thread alone is not a blocker.
- If `package-lock.json` is the only changed file in a review worktree, treat it as likely `npm install` noise, not WIP. Include it in authorized cleanup without another approval step. Do not inspect specific lockfile fields or require proof of which install command caused the change.
- Other staged, unstaged, or untracked changes require approval for the exact path after showing its changes. A general cleanup request does not authorize discarding source edits.
- Preserve an unreferenced detached HEAD with a local backup tag before removal. Old review commits do not require keeping the whole checkout. Do not create tags during a read-only audit.

## Workflow

1. Create a manifest outside any candidate worktree:

   ```bash
   manifest=$(mktemp)
   python3 scripts/detect_stale_worktrees.py --repo "$REPOSITORY" --days 3 --output "$manifest"
   ```

2. Read the manifest and investigate relevant skips. A failed automatic check does not mean the worktree is still needed.

   - Match PR numbers from worktree paths, branch names, or threads as well as branch names and HEAD SHAs. The detector only checks branch names and current PR HEADs, so it can miss an open PR after its HEAD changes.
   - Verify matched PRs with GitHub. Keep worktrees for open or draft PRs. If PR status cannot be checked, retain the affected worktrees.
   - Distinguish an idle shell from a running agent or server in the report. Both still block removal while their working directory is inside the tree. Do not terminate processes as part of cleanup without authorization.
   - Report lockfile-only review changes as install noise. For other dirty worktrees, show exact staged, unstaged, and untracked status lines and ask whether to discard them and delete that path.
   - Filesystem and Git-directory mtimes are not activity signals. Listing or inspecting worktrees can refresh them.

3. Prepare eligible worktrees for the existing cleaner. Its checks are stricter than the completion rules above:

   - For a detached HEAD without a preserving branch or tag, create a local tag such as `worktree-backup/YYYY-MM-DD/<head-sha>`. Verify the tag points to the recorded HEAD, then rerun detection.
   - For confirmed completed work blocked only by age, rerun detection with `--days 0.001`. Keep only the explicitly selected completed paths in that cleanup manifest; do not apply the shorter threshold to unrelated worktrees.
   - Filter manifests by removing ineligible entries. Do not fabricate eligibility flags or erase safety reasons. The cleaner must still revalidate each selected path.
   - The detector labels lockfile-only changes as `review_required`. For an eligible review worktree, the cleanup request authorizes passing its exact path with `--approve-dirty`; no extra question is needed.

4. Run the cleaner only when removal was requested:

   ```bash
   python3 scripts/clean_stale_worktrees.py "$manifest" --confirm REMOVE
   ```

   Pass each eligible lockfile-only review path or explicitly approved dirty path separately:

   ```bash
   python3 scripts/clean_stale_worktrees.py "$manifest" --confirm REMOVE \
     --approve-dirty /exact/eligible/worktree
   ```

   Recheck associated PRs immediately before cleanup, including PRs identified from paths or threads that the scripts cannot match. The cleaner rechecks Git state and process working directories before each removal.

5. Verify and report removed paths, retained paths and reasons, backup tags, and failures. Do not claim cleanup for a failed removal.

An explicit cleanup request authorizes eligible removals, lockfile-only review changes, and local backup tags needed to preserve detached commits. An inspect, detect, list, or audit request is read-only.

## Guardrails

- Never remove the main worktree, a locked worktree, or a worktree with a process working directory inside it.
- Keep open or draft PR worktrees, unfinished work, and unknown states. Recent Git activity alone does not block a confirmed completed review.
- Never remove an unreferenced detached HEAD before preserving it with a verified local tag.
- Use `git worktree remove` through the cleaner. It deletes the checkout and ignored content such as `node_modules`. Use `--force` only through the cleaner's exact-path `--approve-dirty` mechanism.
- Never delete a directory directly, delete a branch, or run `git worktree prune`. Do not push backup tags.
- Fail closed when process, filesystem, manifest, Git, or required PR checks fail.
- Do not install recurring automation unless separately requested.

Run either script with `--help` for its complete interface and exit codes.
