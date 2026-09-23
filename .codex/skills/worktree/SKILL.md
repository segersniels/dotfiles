---
name: worktree
description: Create copy-on-write Git worktrees and prepare them with ignored local .env files and compatible dependencies from the main worktree. Use when creating an isolated checkout for a task or when the user requests a CoW worktree. Does not clean or convert existing worktrees.
---

# Worktree

Create a registered Git worktree with independent files that share disk blocks where supported. Use `git-cow-worktree` for tracked files and the bundled helper for local setup. Existing `git worktree` cleanup tools remain compatible.

## Create

1. Read the repository instructions. Resolve the requested base commit and destination. Use `git worktree list --porcelain` to find the main worktree for local environment files. Preserve the user's base and branch choices. Creating a worktree for an authorized task does not authorize switching the original checkout, committing, or pushing.
2. Locate `git-cow-worktree` on PATH or at `~/.local/bin/git-cow-worktree`. If missing, install the reviewed revision using the existing Go toolchain:

   ```sh
   GOBIN="$HOME/.local/bin" go install github.com/josharian/git-cow-worktree@0f6852cebe494a29dd5fe28eb5077bdb8fda912c
   ```

   If Go is unavailable, report that prerequisite. Do not silently substitute a full disk copy or install a new runtime.
3. Run from the repository, with explicit source, destination and base. Use a new branch for implementation; use `--detach` instead of `-b` when a detached review is intended. Do not force a branch already checked out elsewhere.

   ```sh
   "$HOME/.local/bin/git-cow-worktree" add -v --from "$MAIN_WORKTREE" -b "$BRANCH" "$DESTINATION" "$BASE"
   ```

   Use the actual discovered executable path. This tool creates Git metadata with `--no-checkout`, clones matching tracked content, validates it, and lets Git complete checkout. It skips source edits. Read its clone counts: unsupported filesystems or different volumes can fall back to ordinary checkout. State that fallback; do not claim space savings without successful clones. Keep the destination on the source volume where possible.
4. Verify the target HEAD and clean status. A failed command can leave a registered target: inspect it before retrying; never delete or overwrite an existing destination to make a retry work.

## Prepare local files

Run the helper from this skill's `scripts/` directory, using absolute paths:

```sh
python3 scripts/prepare_worktree.py --source "$MAIN_WORKTREE" --target "$DESTINATION" --copy-deps
```

The helper copies ignored `.env` and `.env.*` regular files from the root and directories represented by tracked files. It preserves relative paths, gives copies owner-only permissions, and never prints values or overwrites an existing file. Tracked templates remain from the target commit. Missing custom env locations can be copied explicitly after checking their target ignore rules. Do not invent credentials or source `.env` files as shell scripts.

Use `--copy-deps` when the source installation is known to work with the project's selected runtime on this machine. The helper compares package manifests, lockfiles, runtime declarations, package-manager configuration and tracked patches before cloning root/workspace `node_modules`. Matching inputs do not prove an installation is complete or current. Verify with the project's relevant validation command. If inputs differ, dependencies are absent, or reuse fails validation, use the repository's normal install command in the target. Keep the prescribed package manager and runtime.

Dependency copies require CoW support; they do not silently fall back to a large ordinary copy. Internal symlinks are retained, absolute internal links are made relative, and links outside the source worktree are rejected. Do not symlink or hard-link the whole dependency folder back to the main worktree. Partial copies after an error are reported and retained for inspection. Do not treat a partial folder as a completed install.

## Finish setup

- Read and run applicable project setup commands needed for the task. Respect migration and build restrictions. Do not copy `.next`, `dist`, running-service locks, or database volumes wholesale.
- Copied env files still reference the same services. Check the project's dev/test settings before running tests or servers. Reuse the intended local services; follow repository Compose instructions. Do not infer database isolation from filesystem isolation.
- When a dev server is needed, check occupied ports and use the project's supported overrides. Update coupled frontend/API URLs in the target configuration when needed. Preserve services already running elsewhere. Verify the server responds on the reported URL.
- Report the target path, branch/HEAD, successful CoW counts, copied env paths, dependency outcome and validation result. Report missing setup plainly. Do not claim the app is ready solely because the files copied.

A skill only controls worktrees created during the agent's work. For a worktree already created by an app, use the preparation helper on its clean target; do not create a second worktree unless the task needs one. This does not retrofit CoW onto its tracked files.

## Cleanup and limits

Use the existing `clean-stale-worktrees` skill when cleanup is requested. CoW worktrees are ordinary registered worktrees; their safety checks and `git worktree remove` still apply. Do not add a second cleanup implementation. Deletion only frees blocks no other copy uses, so apparent directory size is not the amount reclaimed. Existing worktrees do not shrink automatically.

Upstream: https://github.com/josharian/git-cow-worktree
Background: https://commaok.xyz/post/git-cow-worktrees/
