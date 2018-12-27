# If you come from bash you might have to change your $PATH.
export PATH=$HOME/bin:/usr/local/bin:$PATH

# Path to your oh-my-zsh installation.
export ZSH=/Users/niels/.oh-my-zsh

# Remove the username infront of execution
export DEFAULT_USER="$(whoami)"

# Theming
ZSH_THEME="custom-agnoster"
COMPLETION_WAITING_DOTS="true"

# Plugins
plugins=(git docker dotenv osx screen)

source $ZSH/oh-my-zsh.sh

# ZSH styling
zstyle ':completion:*:make:*:targets' call-command true # outputs all possible results for make targets
zstyle ':completion:*:make:*' tag-order targets
zstyle ':completion:*:make:*' group-name '' 
zstyle ':completion:*:descriptions' format '%B%d%b'

# ZSH sources
fpath=(/usr/local/share/zsh-completions $fpath)
source /usr/local/share/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh
source /usr/local/share/zsh-autosuggestions/zsh-autosuggestions.zsh

# Binaries and other exports
export NVM_DIR="$HOME/.nvm"
  . "/usr/local/opt/nvm/nvm.sh"
export PATH="$HOME/.fastlane/bin:$PATH"
export PATH=$PATH:$HOME/go/bin

# Aliases
## General usage
alias reconfigure-git=reconfigure_git
alias gcam="git pull ; git add . ; git commit -m"
alias gp="git push"
alias gpo="git push origin"
alias gpof="git push --force origin"
alias gcp="git checkout --patch"
alias gc="git checkout"
alias jsonify=beautify_json_file
alias docker="supdock"
alias myip=get_public_ip
alias reload="source ~/.zshrc"
alias lego="go run *.go"
alias playground="cd $HOME/playground"
alias dcomp="docker-compose"

# Functions
function get_public_ip () {
  curl ipinfo.io/ip --silent
}

function beautify_json_file () {
  cat $1 |jq '.' > .TEMP
  if [ -s ".TEMP" ]; then
    mv .TEMP $1
  else
    echo "ERR: File $1 contains invalid JSON"
    rm .TEMP
  fi
}

function reconfigure_git () {
  git config --global user.name "Niels Segers"
  git config --global user.email segers.n@hotmail.com
}
