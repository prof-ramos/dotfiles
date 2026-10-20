if [[ -x /opt/homebrew/bin/brew ]]; then
 eval "$(/opt/homebrew/bin/brew shellenv)"
elif [[ -x /usr/local/bin/brew ]]; then
 eval "$(/usr/local/bin/brew shellenv)"
fi
path=("/Applications/Sublime Text.app/Contents/SharedSupport/bin" $path "$HOME/.local/bin")

if [[ -z ${_DOTFILES_EXPORTS_LOADED:-} ]]; then
 source "$HOME/.exports"
 _DOTFILES_EXPORTS_LOADED=1
fi
