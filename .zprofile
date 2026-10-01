
# Added by OrbStack: command-line tools and integration
# This won't be added again if you remove it.
source ~/.orbstack/shell/init.zsh 2>/dev/null || :

# mise: expose tools via shims for non-interactive shells (IDEs, agents, hooks)
eval "$(/opt/homebrew/bin/mise activate zsh --shims)"
