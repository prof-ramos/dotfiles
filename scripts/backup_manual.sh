#!/bin/zsh
set -euo pipefail 2>/dev/null || true

PROJECT_DIR="/Users/gabrielramos/dotfiles"

export PROJECT_DIR
export DO_GIT=1
export DRY_RUN="${DRY_RUN:-0}"

cd "${PROJECT_DIR}"
"${PROJECT_DIR}/scripts/dotfiles_backup.sh"

echo "Backup manual finalizado."


