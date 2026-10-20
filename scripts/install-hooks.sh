#!/bin/zsh
set -euo pipefail
ROOT=${0:A:h:h}
current=$(git -C "$ROOT" config --get core.hooksPath || true)
if [[ -n "$current" && "$current" != .githooks ]]; then
 print -u2 "Existing hooksPath preserved: $current"
 exit 1
fi
git -C "$ROOT" config --local core.hooksPath .githooks
print 'Hooks enabled: staged check before commit; tree/history check before push.'
