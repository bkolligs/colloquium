#!/bin/bash
# Reminds Claude to update CHANGELOG.md when committing

INPUT=$(cat)
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty')

if echo "$COMMAND" | grep -q 'git commit'; then
  echo "Reminder: Update CHANGELOG.md with a one-line summary and PR link before committing." >&2
fi

exit 0
