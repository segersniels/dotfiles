# Review Worktree Bootstrap

Read this reference whenever creating, reusing, or realigning the isolated review worktree.

## Parity definition

The review worktree must reproduce a safe local test setup without contaminating the exact code under review or importing credentials from the checkout where the user invoked the skill.

Parity means:

- Tracked files come from the exact recorded PR HEAD.
- Every tracked `.env.example` at the reviewed HEAD has a neighboring `.env` copied byte-for-byte from that example.
- The same repository-defined runtime and package manager are active.
- Dependencies are installed fresh and successfully in the review worktree before project code runs.

Parity does not mean copying dirty tracked changes, untracked source code, dependency directories, build output, caches, sockets, logs, or arbitrary ignored files. Never make the reviewed code differ from the recorded PR HEAD to imitate the source checkout. Never stage or commit bootstrap output.

## 1. Record only the pre-isolation coordinates

Before creating the worktree, record outside the repository:

- Absolute source-checkout path.
- Current branch, HEAD SHA, upstream, and concise dirty status.
- Repository identity, PR number, base repository and SHA, and head repository and immutable HEAD SHA.

This pre-isolation lookup exists only to identify and create the correct worktree. Do not read the PR body, tickets, comments, reviews, changed-file list or diff, commit messages, checks, or product context yet. Do not inspect repository setup through the source checkout.

Do not automatically copy tracked modifications or arbitrary untracked files. If a dirty tracked file or untracked source file is required to reproduce the user's environment, pause and ask whether it belongs in the test setup. Exact-SHA review and local code mutations cannot both be treated as authoritative.

## 2. Create and verify the exact-SHA worktree

Create or reuse a dedicated worktree detached at the recorded remote PR HEAD. Keep the user's source checkout unchanged.

Before bootstrap, require:

- `HEAD` equals the recorded PR HEAD.
- The index and tracked worktree are clean.
- The destination is the dedicated review worktree, not the source checkout.

If the source checkout is already at the same commit, Git proves tracked-file identity through the shared commit. Still verify both SHAs explicitly. Do not compare or expose ignored secret files through Git output.

After creating and verifying the exact-SHA worktree, read applicable `AGENTS.md` and repository or harness setup instructions from that worktree. Inspect runtime and package-manager selectors such as `packageManager`, lockfiles, version files, and documented bootstrap commands there, not in the source checkout.

Before dependency installation, require that repository or harness worktree setup has been discovered and will be used when present.

Then inventory every tracked file whose basename is exactly `.env.example`. Treat each containing directory as an environment-bearing workspace, including the repository root. Create a parity manifest with each `.env.example -> .env` mapping, file kind, status, and planned action. Never record file contents, environment values, credentials, tokens, or secret-bearing command output.

## 3. Install dependencies before generating workspace environments

Inspect dependency manifests, lockfiles, runtime selectors, package scripts, install hooks, and CI setup before installation. Compare relevant setup changes against the base SHA so untrusted install behavior is visible.

Then run the repository's documented bootstrap or install command with its configured runtime and package manager. Respect its frozen or immutable lockfile convention. Do not substitute another package manager, symlink dependencies from the source checkout, or silently repair the lockfile. Install before generating the workspace `.env` files so install hooks do not receive an application environment they do not need.

If the documented installation requires package-registry authentication, use the existing approved toolchain or credential provider. Do not copy an application `.env` from the source checkout merely because installation needs separate package access.

The dependency install must complete before any test, build, type check, application launch, migration, or reproduction. Record:

- Runtime and package-manager versions.
- Exact install command.
- Exit status and concise result.
- Any tracked file changed by installation.

Use a frozen or immutable install mode when the repository supports it. If installation changes tracked files, the parity gate fails. Record the explicit local side effect, restore only the install-created paths to the reviewed HEAD, and verify cleanliness before continuing. Never keep, stage, commit, or push the generated diff. If installation fails, quote the exact error, try only documented safe setup alternatives, and treat unavailable runtime evidence as a blind spot rather than a PR defect.

## 4. Generate every workspace environment from its example

After dependency installation, use Git's tracked-file list for the reviewed HEAD to find every file whose basename is exactly `.env.example`. Do not scan dependency or build directories. For each tracked example, create `.env` in the same directory:

`<workspace>/.env.example -> <workspace>/.env`

This includes a root `.env.example` and every nested app, package, service, or other workspace that contains one. Do not rely only on package-manager workspace declarations.

For every mapping:

1. Resolve both paths and require them to remain inside the isolated review worktree.
2. Require `.env.example` to be a tracked regular file. Pause on symlinks or special files.
3. Require the destination `.env` to be untracked and ignored at the reviewed HEAD. If it could enter a diff or commit, fail the parity gate instead of creating it.
4. Copy the example bytes directly. Do not interpolate variables or add values.
5. Compare `.env` and `.env.example` byte-for-byte without printing contents or hashes. Record only pass or fail.

If `.env` already exists and is byte-identical, keep it. If it differs, overwrite it only when the review ledger proves this skill generated it and it has not been changed manually. Otherwise, pause or recreate the disposable worktree. Never preserve an unknown `.env` merely to make a test pass.

Never read or copy `.env`, `.env.local`, `.env.production`, `.env.*.local`, or any other environment file from the invoking checkout. Never merge source-checkout values into an example-derived `.env`. Production and staging credentials must not enter the review worktree.

If a workspace needs values that its `.env.example` does not provide, name the affected runtime coverage as blocked. Use a separately authorized safe test credential only when the user explicitly provides that scope. Never fall back to the invoking checkout's environment.

Never copy `.git`, dependency directories such as `node_modules` or a virtual environment, build artifacts, package-manager caches, coverage output, databases, or log files. Install or generate them in the isolated worktree instead.

## 5. Parity gate

Do not execute review scenarios until all applicable checks pass:

- Review worktree HEAD equals the current remote PR HEAD.
- Index and tracked files are clean.
- Every tracked `.env.example` has an ignored, untracked neighboring `.env` that is byte-identical to the example.
- Repository setup completed with the configured toolchain.
- Dependency installation succeeded.
- No environment file or credential was copied from the invoking checkout.
- Runtime paths that need credentials beyond the examples are named as blocked coverage unless the user separately authorized safe test credentials.

Record the gate result in the review ledger without secret values. If a missing parity item can change the review conclusion, stop and ask the user. If it affects only optional coverage, record a precise blind spot and continue through safe verification paths.

## 6. Realign for a new PR HEAD

Before moving the worktree, check whether the new tree tracks, unignores, renames, adds, removes, or conflicts with any `.env.example -> .env` mapping. Pause before checkout if the transition could expose or overwrite an unknown local environment file.

After realignment:

1. Require `HEAD` to equal the new remote PR HEAD.
2. Rebuild the tracked `.env.example` inventory. Create new mappings and refresh changed mappings from the new examples. Require every resulting `.env` to remain ignored, untracked, and byte-identical.
3. Reinspect setup and install hooks changed by the delta.
4. Re-run the configured dependency install when manifests, lockfiles, runtime selectors, workspace layout, patches, or install hooks changed, or when dependency readiness is uncertain.
5. Re-run the parity gate before executing affected verification.

When an existing `.env` differs from the new example, refresh it only if the ledger proves it is an unchanged skill-generated file. Otherwise, recreate the disposable worktree or pause. Never resolve the conflict by copying an environment file from the invoking checkout.

Do not mark the new HEAD reviewed while workspace environment parity or dependency readiness remains unresolved.
