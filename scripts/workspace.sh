#!/bin/zsh
set -euo pipefail
ROOT=${0:A:h:h}
case ${1:-path} in
 path) print -r -- "$ROOT";;
 sublime) exec '/Applications/Sublime Text.app/Contents/SharedSupport/bin/subl' --project "$ROOT/dotfiles.sublime-project";;
 codex) exec codex -C "$ROOT";;
 *) print -u2 'Usage: scripts/workspace.sh path|sublime|codex'; exit 2;;
esac
