---
name: create-worktree
description: "Create an isolated checkout for a non-current branch using `fracture`, not `git worktree add`. Use when Codex needs to review a PR branch, inspect another branch's files, or make edits without touching the current checkout. Fetch the branch locally if needed, use `fracture --no-spawn`, and remove the fracture worktree when finished. Do not use when the target branch is already checked out or no separate worktree is needed."
---

When reviewing a PR, prefer this workflow over reading changed files directly from GitHub when the current checkout is not already on the PR head.

## Process

- Ensure the branch exists by checking the remote and that it exists on the local machine
- If the branch does not exist locally yet you can fetch the remote using `git fetch origin +<branch_name>:<branch_name>`
- Use `fracture --no-spawn <branch_name>` to create a worktree
- If you're purely checking file contents of a branch, also pass `--skip-install` to skip dependency installation (when you don't need to edit code)

## Notes

- Always provide `--no-spawn` to avoid subshell spawn after creation, else you will get stuck
- Worktrees are stored in `~/.fracture/<org>/<slug>` on the filesystem
- When done with a worktree clean it up by running `fracture rm <branch_name>`

## Usage

Usage: fracture [options] [command] [branch]

Quickly create git worktrees to work on multiple branches simultaneously

Arguments:
  branch                      existing branch to checkout, prompts if omitted

Options:
  -b, --branch <name>         create a new branch with this name
  --no-spawn                  create the fracture without spawning a subshell
  -s, --skip-install          skip dependency installation
  -h, --help                  display help for command

Commands:
  list|ls                     List all fractures for the current repository
  enter [name]                Enter an existing fracture
  delete|rm [options] [name]  Delete a fracture
  update                      Update fracture to the latest version