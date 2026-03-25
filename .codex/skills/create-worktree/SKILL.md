---
name: create-worktree
description: "Create a worktree for a given branch. Use when Codex needs to create a worktree for a given branch."
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