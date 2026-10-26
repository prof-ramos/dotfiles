[[ -o interactive ]] || return

# Instant prompt redirects stdout; detect the terminal before loading it.
ZSH_THEME=''
[[ -t 1 ]] && ZSH_THEME='powerlevel10k/powerlevel10k'
[[ -n $ZSH_THEME && -r "${XDG_CACHE_HOME:-$HOME/.cache}/p10k-instant-prompt-${(%):-%n}.zsh" ]] && source "${XDG_CACHE_HOME:-$HOME/.cache}/p10k-instant-prompt-${(%):-%n}.zsh"

if [[ -z ${HOMEBREW_PREFIX:-} ]]; then
 if [[ -x /opt/homebrew/bin/brew ]]; then eval "$(/opt/homebrew/bin/brew shellenv)";
 elif [[ -x /usr/local/bin/brew ]]; then eval "$(/usr/local/bin/brew shellenv)"; fi
fi

# Local credentials remain private, and are loaded only in interactive shells.
[[ -r "$HOME/.zsh_secrets" ]] && source "$HOME/.zsh_secrets"

if [[ -z ${_DOTFILES_EXPORTS_LOADED:-} ]]; then
 source "$HOME/.exports"
 _DOTFILES_EXPORTS_LOADED=1
fi

typeset -U path PATH fpath FPATH cdpath

plugins=(git brew autojump you-should-use)
[[ -d "${HOMEBREW_PREFIX:-/opt/homebrew}/share/zsh/site-functions" ]] && fpath=("${HOMEBREW_PREFIX:-/opt/homebrew}/share/zsh/site-functions" $fpath)
[[ -r "$ZSH/oh-my-zsh.sh" ]] && source "$ZSH/oh-my-zsh.sh"

[[ -r "$HOME/.aliases" ]] && source "$HOME/.aliases"
[[ -r "$HOME/.functions" ]] && source "$HOME/.functions"
cdpath=(. "$HOME/Developer" "$HOME/Documents" $cdpath)

[[ -n $ZSH_THEME && -r "$HOME/.p10k.zsh" ]] && source "$HOME/.p10k.zsh"
[[ -r "${HOMEBREW_PREFIX:-/opt/homebrew}/share/zsh-autosuggestions/zsh-autosuggestions.zsh" ]] && source "${HOMEBREW_PREFIX:-/opt/homebrew}/share/zsh-autosuggestions/zsh-autosuggestions.zsh"
(( $+commands[fnm] )) && eval "$(fnm env --use-on-cd --shell zsh --log-level quiet)"
[[ -s "$HOME/.bun/_bun" ]] && source "$HOME/.bun/_bun"

HISTFILE="$HOME/.zsh_history"
HISTSIZE=50000
SAVEHIST=50000
setopt SHARE_HISTORY HIST_IGNORE_ALL_DUPS HIST_IGNORE_SPACE HIST_EXPIRE_DUPS_FIRST HIST_FIND_NO_DUPS HIST_SAVE_NO_DUPS

[[ -r "$HOME/.zshrc.local" ]] && source "$HOME/.zshrc.local"

# Keep Ghostty integration when reload replaces the shell with exec zsh.
if [[ -n ${GHOSTTY_RESOURCES_DIR:-} && -r "$GHOSTTY_RESOURCES_DIR/shell-integration/zsh/ghostty-integration" ]]; then
 source "$GHOSTTY_RESOURCES_DIR/shell-integration/zsh/ghostty-integration"
fi

[[ -r "${HOMEBREW_PREFIX:-/opt/homebrew}/share/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh" ]] && source "${HOMEBREW_PREFIX:-/opt/homebrew}/share/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh"

export PATH="$HOME/.local/bin:$PATH"
