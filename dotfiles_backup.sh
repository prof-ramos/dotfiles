#!/usr/bin/env bash
set -euo pipefail

# dotfiles_backup.sh — backup seguro e organizado de dotfiles (macOS)
# Destino fixo: /Users/gabrielramos/dotfiles

# --------------------------- Config -------------------------------------------
DEST_DIR="/Users/gabrielramos/dotfiles"
TIMESTAMP="$(date +%Y%m%d-%H%M%S)"
BACKUP_NAME="dotfiles-${HOSTNAME}-${TIMESTAMP}"
WORKDIR=""
DO_BREW=1
DO_VSCODE=1
DO_SSH=0
DO_ENCRYPT=0
DO_GIT=1
DRY_RUN=0

GIT_REMOTE="origin"

INCLUDE_ITEMS=(
  "${HOME}/.zshrc"
  "${HOME}/.p10k.zsh"
  "${HOME}/.gitconfig"
  "${HOME}/.config"
  "${HOME}/Library/Application Support/Code/User/settings.json"
  "${HOME}/Library/Application Support/Code/User/keybindings.json"
  "${HOME}/Library/Application Support/Code/User/snippets"
)

EXCLUDES=(
  "**/*.DS_Store"
  "**/node_modules/**"
  "${HOME}/.ssh/id_*"
  "${HOME}/.ssh/*_key"
)

# --------------------------- Funções ------------------------------------------
info() { echo -e "\033[1;34m[i]\033[0m $*"; }
warn() { echo -e "\033[1;33m[!]\033[0m $*"; }
die()  { echo -e "\033[1;31m[x]\033[0m $*" >&2; exit 1; }

has()  { command -v "$1" >/dev/null 2>&1; }

rsync_copy() {
  local src="$1"; local dest="$2"
  local -a args=(-aHAX --relative)
  for ex in "${EXCLUDES[@]}"; do args+=(--exclude "$ex"); done
  [[ "$DRY_RUN" -eq 1 ]] && args+=(-n -v)
  rsync "${args[@]}" "$src" "$dest"
}

make_manifests() {
  (
    cd "$WORKDIR"
    find . -type f ! -name "manifest.sha256" ! -name "inventory.txt" \
      -exec shasum -a 256 {} \; | sed 's#\./##' > manifest.sha256
    find . -type f | sed 's#\./##' | sort > inventory.txt
  )
}

write_metadata() {
  cat > "${WORKDIR}/metadata.json" <<EOF
{
  "hostname": "${HOSTNAME}",
  "timestamp": "${TIMESTAMP}",
  "user": "${USER}",
  "shell": "${SHELL}"
}
EOF
}

export_brew() {
  [[ "$DO_BREW" -eq 1 ]] || return 0
  if has brew; then
    brew bundle dump --force --file="${WORKDIR}/Brewfile" || warn "Falha ao gerar Brewfile"
  fi
}

export_vscode() {
  [[ "$DO_VSCODE" -eq 1 ]] || return 0
  if has code; then
    code --list-extensions > "${WORKDIR}/vscode-extensions.txt" || warn "Falha ao listar extensões"
  fi
}

export_ssh() {
  [[ "$DO_SSH" -eq 1 ]] || return 0
  local sshdir="${HOME}/.ssh"
  [[ -d "$sshdir" ]] || return 0
  mkdir -p "${WORKDIR}/ssh"
  [[ -f "${sshdir}/config" ]] && cp -p "${sshdir}/config" "${WORKDIR}/ssh/"
  [[ -f "${sshdir}/known_hosts" ]] && cp -p "${sshdir}/known_hosts" "${WORKDIR}/ssh/"
}

pack() {
  mkdir -p "$DEST_DIR"
  local tarball="${DEST_DIR}/${BACKUP_NAME}.tar.gz"
  (
    cd "$(dirname "$WORKDIR")"
    [[ "$DRY_RUN" -eq 1 ]] && { info "[dry-run] tar -czf '$tarball' '$(basename "$WORKDIR")'"; return 0; }
    tar -czf "$tarball" "$(basename "$WORKDIR")"
  )
  echo "$tarball"
}

git_commit_and_push() {
  [[ "$DO_GIT" -eq 1 ]] || return 0
  has git || { warn "git não encontrado"; return 0; }

  local tarball_path="$1"
  (
    cd "$DEST_DIR" || { warn "Falha ao acessar $DEST_DIR"; return 0; }
    [[ -d .git ]] || { warn "Sem repositório Git em $DEST_DIR"; return 0; }

    local tarball_name
    tarball_name="$(basename "$tarball_path")"

    if [[ "$DRY_RUN" -eq 1 ]]; then
      info "[dry-run] git add '$tarball_name' && git commit -m 'backup ${HOSTNAME} ${TIMESTAMP}' && git push ${GIT_REMOTE} <branch>"
      return 0
    fi

    git add "$tarball_name"
    if git diff --cached --quiet; then
      info "Nenhuma mudança para commit"
      return 0
    fi

    local commit_msg
    commit_msg="backup ${HOSTNAME} ${TIMESTAMP}"
    git commit -m "$commit_msg" --no-gpg-sign || { warn "Falha no commit"; return 0; }

    local current_branch
    current_branch="$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo main)"

    # Verifica se o remoto existe
    if git ls-remote --exit-code "$GIT_REMOTE" >/dev/null 2>&1; then
      # Garante upstream na primeira vez
      if git rev-parse --abbrev-ref "@{u}" >/dev/null 2>&1; then
        git push "$GIT_REMOTE" "$current_branch" || warn "Falha no push"
      else
        git push -u "$GIT_REMOTE" "$current_branch" || warn "Falha no push inicial"
      fi
    else
      warn "Remote '$GIT_REMOTE' não configurado"
    fi
  )
}

maybe_git_init() {
  # Mantido apenas para compatibilidade; não inicializa mais dentro do WORKDIR
  return 0
}

# --------------------------- Execução -----------------------------------------
has rsync || die "rsync não encontrado"
WORKDIR="$(mktemp -d "${TMPDIR:-/tmp}/dotfiles.${TIMESTAMP}.XXXX")/${BACKUP_NAME}"
mkdir -p "$WORKDIR"
trap 'rm -rf "$(dirname "$WORKDIR")"' EXIT

info "Copiando dotfiles…"
for path in "${INCLUDE_ITEMS[@]}"; do
  [[ -e "$path" ]] || { warn "não encontrado: $path"; continue; }
  rsync_copy "$path" "$WORKDIR/"
done

export_brew
export_vscode
export_ssh
write_metadata
maybe_git_init
make_manifests

OUTFILE="$(pack)"
[[ -n "$OUTFILE" ]] && git_commit_and_push "$OUTFILE"
info "Backup gerado em: $OUTFILE"


