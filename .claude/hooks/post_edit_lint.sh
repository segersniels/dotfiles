#!/usr/bin/env bash
set -euo pipefail

config_path="$HOME/.claude/hooks/assets/oxlint.config.json"
message="Found style warnings in edited JS/TS files. Only fix diagnostics that overlap the lines you actually edited in this turn. Leave unrelated existing warnings alone, even if oxlint reports them from the same file. If a diagnostic is not clearly tied to your edit, ignore it and continue."
failure_message="oxlint failed while checking edited JS/TS files."

command -v jq >/dev/null || exit 0
[[ -f "$config_path" ]] || exit 0

oxlint_cmd=(npx --yes oxlint@latest)
hook_input=$(cat)
file=$(jq -r '.tool_input.file_path // ""' <<<"$hook_input")
cwd=$(jq -r '.cwd // env.PWD' <<<"$hook_input")

[[ -n "$file" ]] || exit 0

case "$file" in
  *.js|*.jsx|*.mjs|*.cjs|*.ts|*.tsx|*.mts|*.cts) ;;
  *) exit 0 ;;
esac

case "$file" in
  */node_modules/*|*/.next/*|*/dist/*|*/build/*|*/coverage/*|*/.turbo/*) exit 0 ;;
esac

[[ "$file" = /* ]] || file="$cwd/$file"
[[ -f "$file" ]] || exit 0

set +e
output=$("${oxlint_cmd[@]}" -c "$config_path" --format json --no-error-on-unmatched-pattern "$file" 2>&1)
status=$?
diagnostic_count=$(jq -r '.diagnostics | length' <<<"$output" 2>/dev/null)
set -e

if [[ "$diagnostic_count" =~ ^[0-9]+$ ]] && (( diagnostic_count == 0 && status == 0 )); then
  exit 0
fi

[[ -n "$output" ]] || output="oxlint exited with status $status and no output."

if [[ "$diagnostic_count" =~ ^[0-9]+$ ]] && (( diagnostic_count > 0 )); then
  reason="$message"
else
  reason="$failure_message"
fi

jq -n \
  --arg message "$reason" \
  --arg output "$output" \
  '{
    decision: "block",
    reason: $message,
    hookSpecificOutput: {
      hookEventName: "PostToolUse",
      additionalContext: ($message + "\n\n" + $output)
    }
  }'
