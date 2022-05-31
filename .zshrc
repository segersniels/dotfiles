# If you come from bash you might have to change your $PATH.
export PATH=$HOME/bin:/usr/local/bin:$PATH

# Path to your oh-my-zsh installation.
export ZSH=$HOME/.oh-my-zsh

# Remove the username infront of execution
export DEFAULT_USER="$(whoami)"

# Theming
ZSH_THEME="avit"

# Plugins
plugins=(git docker macos screen)

# Oh My Zsh
export ZSH_DISABLE_COMPFIX=true
source $ZSH/oh-my-zsh.sh
source /opt/homebrew/share/zsh-autosuggestions/zsh-autosuggestions.zsh

# Evals
eval $(thefuck --alias)

# ZSH styling
zstyle ':completion:*:make:*:targets' call-command true # outputs all possible results for make targets
zstyle ':completion:*:make:*' tag-order targets
zstyle ':completion:*:make:*' group-name ''
zstyle ':completion:*:descriptions' format '%B%d%b'

# Title
ZSH_THEME_TERM_TITLE_IDLE="%~"

# Aliases
## Git
alias gcam="git add . ; gitmoji -c"
alias gcamp="git add -p ; gitmoji -c"
alias gp="git push"
alias gpo="git push origin"
alias gpof="git push --force origin"
alias gcp="git checkout --patch"
alias gc="git checkout"
alias gbd="git branch --merged origin/master | grep -v master | xargs git branch -d"

## General usage
alias docker="supdock"
alias reload="source ~/.zshrc"
alias playground="cd $HOME/playground"
alias personal="cd $HOME/personal"
alias dcomp="docker compose"
alias zshrc="code $HOME/.zshrc"
alias search="history |grep"
alias gifify=convert_to_gif
alias hyperconfig="code $HOME/.hyper.js"
alias clean-ds-store="find . -name ".DS_Store" -delete"
alias rosetta="arch -x86_64"
alias lipsum=lipsum

# Functions
function convert_to_gif() {
  filename=$(basename -- "$1")
  output="${filename%.*}.gif"
  ffmpeg -i $1 -pix_fmt rgb8 -r 10 $output        # convert to gif
  gifsicle -i $output -O3 --colors 256 -o $output # optimize
}

function lipsum() {
  echo $(curl -s 'https://www.lipsum.com/feed/json?what=paras&amount=1' | jq -r .feed.lipsum) | pbcopy
}

# Exports
## NVM
export NVM_DIR="$HOME/.nvm"
[ -s "/opt/homebrew/opt/nvm/nvm.sh" ] && . "/opt/homebrew/opt/nvm/nvm.sh"                                       # This loads nvm
[ -s "/opt/homebrew/opt/nvm/etc/bash_completion.d/nvm" ] && . "/opt/homebrew/opt/nvm/etc/bash_completion.d/nvm" # This loads nvm bash_completion

## Binaries and other exports
export PATH="$HOME/.fastlane/bin:$PATH"
export PATH=$PATH:$HOME/go/bin
export PATH="$HOME/.yarn/bin:$HOME/.config/yarn/global/node_modules/.bin:$PATH"
export PATH=/opt/homebrew/bin:$PATH
