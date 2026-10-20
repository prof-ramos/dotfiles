[[ -o interactive ]] || return
# Local credentials remain private, and are loaded only in interactive shells.
[[ -r "$HOME/.zsh_secrets" ]] && source "$HOME/.zsh_secrets"
if [[ -z ${HOMEBREW_PREFIX:-} ]]; then
 if [[ -x /opt/homebrew/bin/brew ]]; then eval "$(/opt/homebrew/bin/brew shellenv)";
 elif [[ -x /usr/local/bin/brew ]]; then eval "$(/usr/local/bin/brew shellenv)"; fi
fi
if [[ -z ${_DOTFILES_EXPORTS_LOADED:-} ]]; then
 source "$HOME/.exports"
 _DOTFILES_EXPORTS_LOADED=1
fi
typeset -U path PATH fpath FPATH cdpath
[[ -t 1 && -r "${XDG_CACHE_HOME:-$HOME/.cache}/p10k-instant-prompt-${(%):-%n}.zsh" ]] && source "${XDG_CACHE_HOME:-$HOME/.cache}/p10k-instant-prompt-${(%):-%n}.zsh"
ZSH_THEME=''
[[ -t 1 ]] && ZSH_THEME='powerlevel10k/powerlevel10k'
plugins=(git brew autojump jump you-should-use)
[[ -d "${HOMEBREW_PREFIX:-/opt/homebrew}/share/zsh/site-functions" ]] && fpath=("${HOMEBREW_PREFIX:-/opt/homebrew}/share/zsh/site-functions" $fpath)
[[ -r "$ZSH/oh-my-zsh.sh" ]] && source "$ZSH/oh-my-zsh.sh"
source "$HOME/.aliases"
source "$HOME/.functions"
cdpath=(. "$HOME/Developer" "$HOME/Documents" $cdpath)
[[ -t 1 && -r "$HOME/.p10k.zsh" ]] && source "$HOME/.p10k.zsh"
[[ -r "${HOMEBREW_PREFIX:-/opt/homebrew}/share/zsh-autosuggestions/zsh-autosuggestions.zsh" ]] && source "${HOMEBREW_PREFIX:-/opt/homebrew}/share/zsh-autosuggestions/zsh-autosuggestions.zsh"
(( $+commands[fnm] )) && eval "$(fnm env --use-on-cd --shell zsh --log-level quiet)"
[[ -s "$HOME/.bun/_bun" ]] && source "$HOME/.bun/_bun"
HISTFILE="$HOME/.zsh_history"
HISTSIZE=50000
SAVEHIST=50000
setopt SHARE_HISTORY HIST_IGNORE_ALL_DUPS HIST_IGNORE_SPACE
[[ -r "$HOME/.zshrc.local" ]] && source "$HOME/.zshrc.local"
[[ -r "${HOMEBREW_PREFIX:-/opt/homebrew}/share/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh" ]] && source "${HOMEBREW_PREFIX:-/opt/homebrew}/share/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh"
:
