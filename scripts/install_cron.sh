#!/bin/zsh
set -euo pipefail 2>/dev/null || true

PROJECT_DIR="/Users/gabrielramos/dotfiles"
LOG_DIR="${PROJECT_DIR}/logs"
mkdir -p "${LOG_DIR}"

CRON_LINE="15 2 * * * SHELL=/bin/zsh PATH=/opt/homebrew/bin:/usr/local/bin:/bin:/usr/bin PROJECT_DIR=${PROJECT_DIR} DO_GIT=1 ${PROJECT_DIR}/scripts/dotfiles_backup.sh >> ${LOG_DIR}/cron.log 2>&1"

TMP_CRON=$(mktemp)
crontab -l 2>/dev/null | grep -v "dotfiles_backup.sh" > "${TMP_CRON}" || true
echo "${CRON_LINE}" >> "${TMP_CRON}"
crontab "${TMP_CRON}"
rm -f "${TMP_CRON}"

echo "Cron instalado. Próxima execução diária às 02:15. Logs em ${LOG_DIR}/cron.log"


