#!/usr/bin/env zsh
# Install or verify shell dependencies pinned by scripts/zsh-deps.lock.
set -euo pipefail

if (( $# != 1 )) || [[ "$1" != "--install" && "$1" != "--verify" ]]; then
  echo "Uso: $0 --install | --verify" >&2
  exit 1
fi
mode="$1"
SCRIPT_DIR="${0:A:h}"
ZSH_DEPS_LOCK="$SCRIPT_DIR/zsh-deps.lock"
ZSH_DIR="$HOME/.oh-my-zsh"
ZSH_CUSTOM="$ZSH_DIR/custom"

lookup_locked_sha() {
  local repository="$1"
  local repo sha
  if [[ ! -r "$ZSH_DEPS_LOCK" ]]; then
    echo "❌ Lock de dependências do Zsh ausente: $ZSH_DEPS_LOCK" >&2
    echo "   Atualize scripts/zsh-deps.lock e rode o instalador novamente." >&2
    return 1
  fi
  while read -r repo sha; do
    [[ -z "$repo" || "$repo" == \#* ]] && continue
    if [[ "$repo" == "$repository" ]]; then
      printf '%s\n' "$sha"
      return 0
    fi
  done < "$ZSH_DEPS_LOCK"
  echo "❌ SHA não encontrado em $ZSH_DEPS_LOCK para $repository" >&2
  echo "   Atualize o lock com o commit desejado e rode o instalador novamente." >&2
  return 1
}

clone_if_missing() {
  local repository="$1"
  local destination="$2"
  local marker="$3"
  local expected_sha actual_sha
  local staging

  expected_sha="$(lookup_locked_sha "$repository")" || return 1

  if [[ -e "$destination" ]]; then
    if [[ ! -r "$marker" ]]; then
      echo "❌ Dependência do Zsh existente, mas incompleta: $destination" >&2
      echo "   Faça backup e remova ou renomeie esse diretório antes de rodar novamente." >&2
      return 1
    fi
    actual_sha="$(git -C "$destination" rev-parse HEAD 2>/dev/null || true)"
    if [[ "$actual_sha" != "$expected_sha" ]]; then
      echo "❌ SHA de $destination não confere com scripts/zsh-deps.lock" >&2
      echo "   esperado: $expected_sha" >&2
      echo "   atual:    ${actual_sha:-<ausente>}" >&2
      echo "   Atualize o lock ou substitua o diretório e rode novamente." >&2
      return 1
    fi
    return 0
  fi

  if [[ "$mode" == "--verify" ]]; then
    echo "❌ Dependência do Zsh ausente: $destination" >&2
    return 1
  fi

  mkdir -p "$(dirname "$destination")"
  staging="$(mktemp -d "${destination}.staging.XXXXXX")"
  if ! {
    git init "$staging" &&
    git -C "$staging" remote add origin "$repository" &&
    git -C "$staging" fetch --depth=1 origin "$expected_sha" &&
    git -C "$staging" checkout --detach FETCH_HEAD &&
    mv "$staging" "$destination"
  }; then
    rm -rf "$staging"
    return 1
  fi
}

require_shell_dependency() {
  local dependency_path="$1"
  if [[ ! -r "$dependency_path" ]]; then
    echo "❌ Dependência do Zsh incompleta ou ausente: $dependency_path" >&2
    return 1
  fi
}

clone_if_missing "https://github.com/ohmyzsh/ohmyzsh.git" "$ZSH_DIR" \
  "$ZSH_DIR/oh-my-zsh.sh"
require_shell_dependency "$ZSH_DIR/oh-my-zsh.sh"
if [[ "$mode" == "--install" ]]; then
  mkdir -p "$ZSH_CUSTOM/themes" "$ZSH_CUSTOM/plugins"
fi
clone_if_missing "https://github.com/romkatv/powerlevel10k.git" \
  "$ZSH_CUSTOM/themes/powerlevel10k" \
  "$ZSH_CUSTOM/themes/powerlevel10k/powerlevel10k.zsh-theme"
require_shell_dependency "$ZSH_CUSTOM/themes/powerlevel10k/powerlevel10k.zsh-theme"
clone_if_missing "https://github.com/MichaelAquilina/zsh-you-should-use.git" \
  "$ZSH_CUSTOM/plugins/you-should-use" \
  "$ZSH_CUSTOM/plugins/you-should-use/you-should-use.plugin.zsh"
require_shell_dependency "$ZSH_CUSTOM/plugins/you-should-use/you-should-use.plugin.zsh"

echo "Shell dependencies ${mode#--} complete."
