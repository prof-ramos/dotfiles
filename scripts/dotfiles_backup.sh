#!/bin/zsh

set -euo pipefail 2>/dev/null || true
set -euo
setopt pipefail 2>/dev/null || true

# ==============================================
# dotfiles_backup.sh
#
# macOS (zsh) backup de dotfiles para o diretório do projeto.
# Gera tarball nomeado: dotfiles-${HOSTNAME}-${TIMESTAMP}.tar.gz
# Exporta Brewfile e extensões do VS Code, inventário e manifestos.
# Opcionalmente faz commit/push no Git quando DO_GIT=1.
# Respeita DRY_RUN=1 para apenas simular.
# ==============================================

# Preferir caminhos absolutos; permite override por variável de ambiente
PROJECT_DIR="${PROJECT_DIR:-/Users/gabrielramos/dotfiles}"
BACKUP_DIR="${PROJECT_DIR}"

# Variáveis de controle
DRY_RUN="${DRY_RUN:-0}"
DO_GIT="${DO_GIT:-0}"

# Descobrir caminhos de ferramentas de forma resiliente
BREW_BIN="${BREW_BIN:-}"
if [[ -z "${BREW_BIN}" ]]; then
  if command -v brew >/dev/null 2>&1; then
    BREW_BIN="$(command -v brew)"
  elif [[ -x "/opt/homebrew/bin/brew" ]]; then
    BREW_BIN="/opt/homebrew/bin/brew"
  else
    BREW_BIN=""
  fi
fi

CODE_BIN="${CODE_BIN:-}"
if [[ -z "${CODE_BIN}" ]]; then
  if command -v code >/dev/null 2>&1; then
    CODE_BIN="$(command -v code)"
  elif [[ -x "/opt/homebrew/bin/code" ]]; then
    CODE_BIN="/opt/homebrew/bin/code"
  elif [[ -x "/usr/local/bin/code" ]]; then
    CODE_BIN="/usr/local/bin/code"
  else
    CODE_BIN=""
  fi
fi

HOSTNAME_SHORT="$(hostname -s || uname -n)"
TIMESTAMP="$(/bin/date -u +%Y%m%dT%H%M%SZ)"
TARBALL_NAME="dotfiles-${HOSTNAME_SHORT}-${TIMESTAMP}.tar.gz"
TARBALL_PATH="${BACKUP_DIR}/${TARBALL_NAME}"

INCLUDE_LIST="${PROJECT_DIR}/backup/include.lst"
EXCLUDE_LIST="${PROJECT_DIR}/backup/exclude.lst"

LOG() { printf "%s\n" "$*"; }

abort() {
  LOG "ERRO: $*" 1>&2
  exit 1
}

ensure_prereqs() {
  [[ -d "${PROJECT_DIR}" ]] || abort "Diretório do projeto não encontrado: ${PROJECT_DIR}"
  if [[ "${SKIP_HOME:-0}" != "1" ]]; then
    [[ -f "${INCLUDE_LIST}" ]] || abort "Lista de inclusão ausente: ${INCLUDE_LIST}"
    [[ -f "${EXCLUDE_LIST}" ]] || abort "Lista de exclusão ausente: ${EXCLUDE_LIST}"
  fi
}

make_staging() {
  STAGING_DIR=$(mktemp -d /tmp/dotfiles_backup.XXXXXX)
  INVENTORY_FILE="${STAGING_DIR}/inventory.txt"
  MANIFEST_FILE="${STAGING_DIR}/manifest.sha256"
  METADATA_DIR="${STAGING_DIR}/.backup_meta"
  mkdir -p "${METADATA_DIR}"
}

collect_home_items() {
  if [[ "${SKIP_HOME:-0}" == "1" ]]; then
    LOG "SKIP_HOME=1 — pulando coleta de itens do HOME"
    return 0
  fi
  LOG "Coletando itens do HOME (${HOME}) via rsync (listas: include/exclude)"
  mkdir -p "${STAGING_DIR}/home"
  # Executa rsync a partir do $HOME usando include/exclude para copiar apenas o necessário
  pushd "${HOME}" >/dev/null
  if [[ "${DRY_RUN}" == "1" ]]; then
    rsync -an --prune-empty-dirs \
      --include-from "${INCLUDE_LIST}" \
      --exclude-from "${EXCLUDE_LIST}" \
      --exclude='*' ./ "${STAGING_DIR}/home/"
  else
    rsync -a --prune-empty-dirs \
      --include-from "${INCLUDE_LIST}" \
      --exclude-from "${EXCLUDE_LIST}" \
      --exclude='*' ./ "${STAGING_DIR}/home/"
  fi
  popd >/dev/null
}

export_brewfile() {
  if [[ "${SKIP_BREW:-0}" == "1" ]]; then
    LOG "SKIP_BREW=1 — pulando export do Brewfile"
    return 0
  fi
  if [[ -n "${BREW_BIN}" && -x "${BREW_BIN}" ]]; then
    LOG "Exportando Brewfile"
    if [[ "${DRY_RUN}" == "1" ]]; then
      : # no-op em dry run
    else
      "${BREW_BIN}" bundle dump --force --file "${STAGING_DIR}/Brewfile" || LOG "Aviso: falha ao gerar Brewfile"
      # Copia uma versão para o diretório do projeto para versionar
      cp -f "${STAGING_DIR}/Brewfile" "${PROJECT_DIR}/Brewfile" 2>/dev/null || true
    fi
  else
    LOG "Aviso: Homebrew não encontrado em ${BREW_BIN}; pulando Brewfile"
  fi
}

export_vscode_extensions() {
  if [[ "${SKIP_VSCODE:-0}" == "1" ]]; then
    LOG "SKIP_VSCODE=1 — pulando export de extensões do VS Code"
    return 0
  fi
  if [[ -n "${CODE_BIN}" && -x "${CODE_BIN}" ]]; then
    LOG "Exportando extensões do VS Code"
    if [[ "${DRY_RUN}" == "1" ]]; then
      :
    else
      "${CODE_BIN}" --list-extensions > "${STAGING_DIR}/vscode-extensions.txt" || LOG "Aviso: falha ao listar extensões VS Code"
      cp -f "${STAGING_DIR}/vscode-extensions.txt" "${PROJECT_DIR}/vscode-extensions.txt" 2>/dev/null || true
    fi
  else
    LOG "Aviso: 'code' CLI do VS Code não encontrado; pulando export de extensões"
  fi
}

write_metadata() {
  LOG "Gerando inventário e manifestos"
  if [[ "${DRY_RUN}" == "1" ]]; then
    :
  else
    {
      printf "host: %s\n" "${HOSTNAME_SHORT}"
      printf "timestamp_utc: %s\n" "${TIMESTAMP}"
      printf "script: dotfiles_backup.sh\n"
    } > "${METADATA_DIR}/meta.yml"

    (cd "${STAGING_DIR}" && env LC_ALL=C find . -type f -print0 | xargs -0 stat -f "%N|%z" | sort) > "${INVENTORY_FILE}" || true

    # Manifesto SHA-256
    if command -v shasum >/dev/null 2>&1; then
      (cd "${STAGING_DIR}" && env LC_ALL=C find . -type f -print0 | xargs -0 shasum -a 256 | sort) > "${MANIFEST_FILE}" || true
    elif command -v /sbin/shasum >/dev/null 2>&1; then
      (cd "${STAGING_DIR}" && env LC_ALL=C find . -type f -print0 | xargs -0 /sbin/shasum -a 256 | sort) > "${MANIFEST_FILE}" || true
    else
      LOG "Aviso: shasum não encontrado; manifesto SHA-256 não gerado"
    fi
  fi
}

make_tarball() {
  LOG "Empacotando em: ${TARBALL_PATH}"
  if [[ "${DRY_RUN}" == "1" ]]; then
    LOG "DRY_RUN=1 — pulando criação do tarball"
  else
    mkdir -p "${BACKUP_DIR}"
    # Empacota conteúdo do staging
    (cd "${STAGING_DIR}" && tar -czf "${TARBALL_PATH}" .)
  fi
}

git_commit_and_push() {
  if [[ "${DO_GIT}" != "1" ]]; then
    LOG "DO_GIT!=1 — não será feito commit/push"
    return 0
  fi
  LOG "Fazendo commit e push para o repositório git"
  if [[ "${DRY_RUN}" == "1" ]]; then
    LOG "DRY_RUN=1 — pulando git add/commit/push"
    return 0
  fi
  pushd "${PROJECT_DIR}" >/dev/null
  if [[ -f "${TARBALL_PATH}" ]]; then
    git add "${TARBALL_PATH}"
  fi
  if [[ -f "${PROJECT_DIR}/Brewfile" ]]; then
    git add "${PROJECT_DIR}/Brewfile"
  fi
  # Não versionamos diretório staging; apenas tarball e artefatos persistentes (se houverem)
  if ! git diff --cached --quiet; then
    git commit -m "backup ${HOSTNAME_SHORT} ${TIMESTAMP}"
    git push origin HEAD
  else
    LOG "Nada para commitar"
  fi
  popd >/dev/null
}

cleanup() {
  if [[ -n "${STAGING_DIR:-}" && -d "${STAGING_DIR}" ]]; then
    rm -rf "${STAGING_DIR}"
  fi
}

main() {
  LOG "Iniciando backup de dotfiles — host: ${HOSTNAME_SHORT}, ts: ${TIMESTAMP}"
  ensure_prereqs
  make_staging
  trap cleanup EXIT
  collect_home_items
  export_brewfile
  export_vscode_extensions
  write_metadata
  make_tarball
  git_commit_and_push
  LOG "Backup concluído"
}

main "$@"


