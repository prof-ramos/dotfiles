#!/bin/zsh
set -euo pipefail
ROOT=${0:A:h}
stage=''
dry=0
selected_modules=()
usage() { print 'Uso: ./bootstrap.sh --stage apps|shell|macos|visual|all [--module personal|development|security|cloud|media] [--dry-run]'; }
(( $# )) || { usage; exit 0; }
while (( $# )); do
 case $1 in
  --stage) (( $# >= 2 )) || exit 2; stage=$2; shift 2;;
  --module) (( $# >= 2 )) || exit 2; case $2 in personal|development|security|cloud|media) selected_modules+=($2);; *) print -u2 'Módulo inválido'; exit 2;; esac; shift 2;;
  --dry-run) dry=1; shift;;
  --help) usage; exit 0;;
  *) usage >&2; exit 2;;
 esac
done
case $stage in apps|shell|macos|visual|all) ;; *) usage >&2; exit 2;; esac
stages=($stage)
[[ $stage == all ]] && stages=(apps shell macos visual)
if (( dry )); then
 preview_args=(--stage "$stage" --target "$HOME")
 for m in $selected_modules; do preview_args+=(--module "$m"); done
 exec python3 "$ROOT/scripts/preview.py" $preview_args
fi
[[ $(uname -s) == Darwin ]] || { print -u2 'Apenas macOS'; exit 1; }
for s in $stages; do
 case $s in
 apps) /bin/zsh -f "$ROOT/scripts/apps.sh" $selected_modules;;
 shell) /bin/zsh -f "$ROOT/scripts/install-shell-deps.sh" --install; python3 "$ROOT/scripts/links.py" apply --target "$HOME";;
 macos) python3 "$ROOT/scripts/macos-preferences.py" apply;;
 visual) swift "$ROOT/scripts/apply-folder-icons.swift" --map "$ROOT/macos/folder-icons.json" --home "$HOME"; python3 "$ROOT/scripts/default-apps.py" apply;;
 esac
done
print 'Concluído: etapas selecionadas.'
