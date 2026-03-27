---
name: create-worktree
description: "Create an isolated checkout for a non-current branch using `fracture`, not `git worktree add`. Use when Codex needs to review a PR branch, inspect another branch's files, or make edits without touching the current checkout. Fetch the branch locally if needed, use `fracture --no-spawn`, and remove the fracture worktree when finished. Do not use when the target branch is already checked out or no separate worktree is needed."
---

## Process

- Ensure the branch exists by checking the remote and that it exists on the local machine
- If the branch does not exist locally yet you can fetch the remote using `git fetch origin +<branch_name>:<branch_name>`
- Use `fracture --no-spawn <branch_name>` to create a worktree
- If you're purely checking file contents of a branch, also pass `--skip-install` to skip dependency installation (when you don't need to edit code)

## Notes

- Always provide `--no-spawn` to avoid subshell spawn after creation, else you will get stuck
- Worktrees are stored in `~/.fracture/<org>/<slug>` on the filesystem
- When done with a worktree clean it up by running `fracture rm <branch_name>`
