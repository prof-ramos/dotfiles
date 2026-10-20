#!/bin/zsh
set -euo pipefail
ROOT=${0:A:h:h}
if ! xcode-select -p >/dev/null 2>&1; then
 xcode-select --install
 print -u2 'Conclua a instalação de Command Line Tools e execute novamente.'
 exit 1
fi
if ! command -v brew >/dev/null; then
 if [[ -x /opt/homebrew/bin/brew ]]; then eval "$(/opt/homebrew/bin/brew shellenv)"; else
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
  eval "$(/opt/homebrew/bin/brew shellenv)"
 fi
fi
brew bundle --file="$ROOT/Brewfile"
for module in "$@"; do
 case $module in personal|development|security|cloud|media) ;; *) exit 2;; esac
 brew bundle --file="$ROOT/modules/$module/Brewfile"
done
