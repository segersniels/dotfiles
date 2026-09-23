# CI Diagnosis

Read this when the watcher reports failed checks or proposes a retry.

Inspect failed-job logs before deciding what to do. A workflow may still be running when one job has already failed; use the watcher's `failed_jobs`, `job_id`, and `logs_endpoint` to diagnose immediately. See [GitHub API notes](github-api-notes.md#failed-log-inspection) for log commands.

## Fix, retry, or wait

- Treat a failure as branch-related when logs and the changed behavior establish that the PR caused it. Examples include compile, lint, typecheck, test, or snapshot failures tied to the change.
- Treat runner provisioning, registry/network outages, and known unrelated nondeterministic failures as likely flakes or infrastructure failures. Do not change tests, build scripts, CI configuration, or dependency pins merely to make unrelated failures pass.
- If classification is uncertain, inspect the specific failed path before choosing a retry.
- For a branch-related fix, follow [scope and safe fixes](safe-fixes.md).
- Retry likely flakes only when `actions` includes `retry_failed_checks` and no imminent fix will replace the SHA. If a fix is ready, push it and let the new CI run supersede the old failure.

To retry, stop the active watcher and run:

```bash
python3 "<babysit-skill-directory>/scripts/gh_pr_watch.py" --pr <pr-url> --retry-failed-now
```

Resolve the skill directory as described in `SKILL.md`, then restart `--watch` in the same turn. The watcher tracks retry cycles per SHA; honor its configured budget (default 3) rather than bypassing it with manual reruns.

Wait for pending jobs when no action is available. Exhausted retries, persistent infrastructure failures, or missing permissions require a user-help handoff when no independent authorized work can proceed.
