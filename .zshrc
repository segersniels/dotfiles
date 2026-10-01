## Shell

# Completions (OrbStack and Homebrew add to fpath, so load them before compinit)
source ~/.orbstack/shell/init.zsh 2>/dev/null || :
fpath=(/opt/homebrew/share/zsh/site-functions $fpath)
autoload -Uz compinit && compinit

setopt auto_menu complete_in_word always_to_end
zstyle ':completion:*' menu select
zstyle ':completion:*' matcher-list 'm:{[:lower:][:upper:]}={[:upper:][:lower:]}' 'r:|=*' 'l:|=* r:|=*'
zstyle ':completion:*' special-dirs true
zstyle ':completion:*' list-colors ''

# History
HISTFILE="$HOME/.zsh_history"
HISTSIZE=50000
SAVEHIST=10000
setopt extended_history hist_expire_dups_first hist_ignore_dups hist_ignore_space hist_verify share_history

# Navigation
setopt auto_cd auto_pushd pushd_ignore_dups interactive_comments

# Keys: emacs mode, up/down search history by typed prefix
bindkey -e
autoload -U up-line-or-beginning-search down-line-or-beginning-search
zle -N up-line-or-beginning-search
zle -N down-line-or-beginning-search
bindkey '^[[A' up-line-or-beginning-search
bindkey '^[[B' down-line-or-beginning-search
bindkey '^[[1;5C' forward-word
bindkey '^[[1;5D' backward-word
bindkey '^[[Z' reverse-menu-complete

export CLICOLOR=1

## Alias

alias personal='cd $HOME/personal'
alias reload='source $HOME/.zshrc'
alias dcomp='docker compose'
alias search='history |grep'
alias docker='supdock'
alias zshrc='vi $HOME/.zshrc'
alias gcam='git add . && cmt commit'
alias gcamp='git add -p && cmt commit'
alias gp='git push'
alias dotfiles='cd $HOME/personal/dotfiles'
alias code="cursor"
alias vi="nvim"
alias -- -='cd -'
alias ll='ls -lh'
alias gpf='git push --force-with-lease --force-if-includes'
alias history='fc -l 1'
alias grep='grep --color=auto'

## Exports

export EDITOR="cursor"
export GIT_EDITOR="vim"

## Secrets

if [ -f $HOME/.secrets ]; then
  source $HOME/.secrets
fi

## Functions

function gifify() {
  # Extract the filename without its path
  filename=$(basename -- "$1")
  # Remove the file extension to prepare the output name
  output="${filename%.*}.gif"

  # Step 1: Generate a palette
  palette="/tmp/palette.png"
  filters="fps=10"
  ffmpeg -i "$1" -vf "$filters,palettegen" -y $palette

  # Step 2: Use the palette to create the gif
  ffmpeg -i "$1" -i $palette -lavfi "$filters [x]; [x][1:v] paletteuse" -y $output

  # Step 3: Optimize gif
  gifsicle -i $output -O3 --colors 256 -o $output
}

function gfr() {
  # Fetch remote to local for easier worktree management
  git fetch origin +$1:$1
}

function gcpr() {
  # Cherry pick a range of commits incl. the start commit
  if [ $# -ne 2 ]; then
    echo "Usage: gcpr FIRST_COMMIT LAST_COMMIT"
    return 2
  fi

  git cherry-pick "$1^..$2"
}

## Customization

zstyle ':completion:*:make:*:targets' call-command true # outputs all possible results for make targets
zstyle ':completion:*:make:*' tag-order targets
zstyle ':completion:*:make:*' group-name ''
zstyle ':completion:*:descriptions' format '%B%d%b'

# Tinybird
export PATH="$HOME/.local/bin:$PATH"

# bun completions
[ -s "/Users/segersniels/.bun/_bun" ] && source "/Users/segersniels/.bun/_bun"

# bun
export BUN_INSTALL="$HOME/.bun"
export PATH="$BUN_INSTALL/bin:$PATH"

# mise
eval "$(mise activate zsh)"

# opencode
export PATH=/Users/segersniels/.opencode/bin:$PATH

# android
export JAVA_HOME=/Library/Java/JavaVirtualMachines/zulu-17.jdk/Contents/Home
export ANDROID_HOME=$HOME/Library/Android/sdk
export PATH=$PATH:$ANDROID_HOME/emulator:$ANDROID_HOME/platform-tools:$ANDROID_HOME/cmdline-tools/latest/bin

# >>> railway initialize >>>
[ -f "$HOME/.railway/env" ] && source "$HOME/.railway/env"
# <<< railway initialize <<<

## Prompt and plugins (keep last)

source /opt/homebrew/share/zsh-autosuggestions/zsh-autosuggestions.zsh
eval "$(starship init zsh)"
