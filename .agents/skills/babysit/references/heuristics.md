# CI Diagnosis

Read this when the watcher reports failed checks.

Inspect failed-job logs before deciding what to do. A workflow may still be running when one job has already failed; diagnose it immediately. For a GitHub Actions check, the URL in the watcher update has the form `.../actions/runs/<run-id>/job/<job-id>`. See [GitHub API notes](github-api-notes.md#failed-log-inspection) for log commands.

## Fix, retry, or wait

- Treat a failure as branch-related when logs and the changed behavior establish that the PR caused it. Examples include compile, lint, typecheck, test, or snapshot failures tied to the change.
- Treat runner provisioning, registry/network outages, and known unrelated nondeterministic failures as likely flakes or infrastructure failures. Do not change tests, build scripts, CI configuration, or dependency pins merely to make unrelated failures pass.
- If classification is uncertain, inspect the specific failed path before choosing a retry.
- For a branch-related fix, follow [scope and safe fixes](safe-fixes.md).
- Retry likely flakes only when no imminent fix will replace the SHA. If a fix is ready, push it and let the new CI run supersede the old failure.

Retry each workflow run at most 3 times. GitHub counts the attempts, so check the count before each retry and keep the watch running:

```bash
gh run view <run-id> --json attempt --jq .attempt
gh run rerun <run-id> --failed
```

Rerun only when `attempt` is 3 or lower. The watcher reports the check again if the rerun fails.

Wait for pending jobs when no action is available. Exhausted retries, persistent infrastructure failures, or missing permissions require a user-help handoff when no independent authorized work can proceed.
