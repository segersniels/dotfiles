#!/usr/bin/env bash
set -euo pipefail

config_path="$HOME/.codex/hooks/assets/oxlint.config.json"
message="Found style warnings in edited JS/TS files. Fix the diagnostics that apply to the current edit, then continue."

command -v jq >/dev/null || exit 0
[[ -f "$config_path" ]] || exit 0

hook_input=$(cat)
command=$(jq -r '.tool_input.command // ""' <<<"$hook_input")
cwd=$(jq -r '.cwd // env.PWD' <<<"$hook_input")

[[ -n "$command" ]] || exit 0

if command -v oxlint >/dev/null; then
  oxlint_cmd=(oxlint)
elif command -v npx >/dev/null; then
  oxlint_cmd=(npx --no-install oxlint)
else
  exit 0
fi

files=()

while IFS= read -r file; do
  [[ -n "$file" ]] || continue

  case "$file" in
    *.js|*.jsx|*.mjs|*.cjs|*.ts|*.tsx|*.mts|*.cts) ;;
    *) continue ;;
  esac

  case "$file" in
    */node_modules/*|*/.next/*|*/dist/*|*/build/*|*/coverage/*|*/.turbo/*) continue ;;
  esac

  if [[ "$file" = /* ]]; then
    absolute_file="$file"
  else
    absolute_file="$cwd/$file"
  fi

  [[ -f "$absolute_file" ]] && files+=("$absolute_file")
done < <(
  awk '
    /^\*\*\* Add File: / {
      sub(/^\*\*\* Add File: /, "")
      print
      next
    }

    /^\*\*\* Update File: / {
      sub(/^\*\*\* Update File: /, "")
      print
      next
    }

    /^\*\*\* Move to: / {
      sub(/^\*\*\* Move to: /, "")
      print
      next
    }
  ' <<<"$command" | sort -u
)

(( ${#files[@]} )) || exit 0

set +e
output=$("${oxlint_cmd[@]}" -c "$config_path" --no-error-on-unmatched-pattern "${files[@]}" 2>&1)
status=$?
set -e

[[ -n "${output//[[:space:]]/}" ]] || exit 0

jq -n \
  --arg message "$message" \
  --arg output "$output" \
  '{
    decision: "block",
    reason: $message,
    hookSpecificOutput: {
      hookEventName: "PostToolUse",
      additionalContext: ($message + "\n\n" + $output)
    }
  }'
