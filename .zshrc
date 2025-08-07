# Path to your oh-my-zsh installation.
export ZSH="$HOME/.oh-my-zsh"

# Set name of the theme to load --- if set to "random", it will
# load a random theme each time oh-my-zsh is loaded, in which case,
# to know which specific one was loaded, run: echo $RANDOM_THEME
# See https://github.com/ohmyzsh/ohmyzsh/wiki/Themes
ZSH_THEME="avit"

# Uncomment the following line to use case-sensitive completion.
# CASE_SENSITIVE="true"

# Uncomment the following line to use hyphen-insensitive completion.
# Case-sensitive completion must be off. _ and - will be interchangeable.
# HYPHEN_INSENSITIVE="true"

# Which plugins would you like to load?
# Standard plugins can be found in $ZSH/plugins/
# Custom plugins may be added to $ZSH_CUSTOM/plugins/
# Example format: plugins=(rails git textmate ruby lighthouse)
# Add wisely, as too many plugins slow down shell startup.
plugins=(git zsh-autosuggestions)

source $ZSH/oh-my-zsh.sh

# User configuration

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
alias nvm="fnm"

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

# fnm
eval "$(fnm env --use-on-cd --shell zsh)"

# The next line updates PATH for the Google Cloud SDK.
if [ -f '/Users/segersniels/Downloads/google-cloud-sdk/path.zsh.inc' ]; then . '/Users/segersniels/Downloads/google-cloud-sdk/path.zsh.inc'; fi

# The next line enables shell command completion for gcloud.
if [ -f '/Users/segersniels/Downloads/google-cloud-sdk/completion.zsh.inc' ]; then . '/Users/segersniels/Downloads/google-cloud-sdk/completion.zsh.inc'; fi

# Claude Code
alias claude="~/.claude/local/claude"

# opencode
export PATH=/Users/segersniels/.opencode/bin:$PATH
