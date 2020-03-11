# If you come from bash you might have to change your $PATH.
export PATH=$HOME/bin:/usr/local/bin:$PATH

# Path to your oh-my-zsh installation.
export ZSH=/Users/nielssegers/.oh-my-zsh

# Remove the username infront of execution
export DEFAULT_USER="$(whoami)"

# Theming
ZSH_THEME="avit"

# Plugins
plugins=(git docker dotenv osx screen zsh-autosuggestions)

export ZSH_DISABLE_COMPFIX=true
source $ZSH/oh-my-zsh.sh

# Fuck
eval $(thefuck --alias)

# ZSH styling
zstyle ':completion:*:make:*:targets' call-command true # outputs all possible results for make targets
zstyle ':completion:*:make:*' tag-order targets
zstyle ':completion:*:make:*' group-name ''
zstyle ':completion:*:descriptions' format '%B%d%b'

# ZSH sources
fpath=(/usr/local/share/zsh-completions $fpath)
source /usr/local/share/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh

# Title
DISABLE_AUTO_TITLE="true"
precmd() { echo -n -e "\033]0;$(basename "$PWD")\007" }

# Aliases
## Git
alias gcam="git add . ; gitmoji -c"
alias gcamp="git add -p ; gitmoji -c"
alias gp="git push"
alias gpo="git push origin"
alias gpof="git push --force origin"
alias gcp="git checkout --patch"
alias gc="git checkout"

## General usage
alias reconfigure-git=reconfigure_git
alias jsonify=beautify_json_file
alias docker="supdock"
alias myip=get_public_ip
alias reload="source ~/.zshrc"
alias lego="go run *.go"
alias playground="cd $HOME/playground"
alias personal="cd $HOME/personal"
alias dcomp="docker-compose"
alias zshrc="code $HOME/.zshrc"
alias search="history |grep"
alias gifify=convert_to_gif

# Functions
function get_public_ip() {
	curl ipinfo.io/ip --silent
}

function beautify_json_file() {
	cat $1 | jq '.' >.TEMP
	if [ -s ".TEMP" ]; then
		mv .TEMP $1
	else
		echo "ERR: File $1 contains invalid JSON"
		rm .TEMP
	fi
}

function reconfigure_git() {
	git config --global user.name "segersniels"
	git config --global user.email segers.n@hotmail.com
}

function convert_to_gif() {
	filename=$(basename -- "$1")
	output="${filename%.*}.gif"
	ffmpeg -i $1 -pix_fmt rgb8 -r 10 $output # convert to gif
	gifsicle -O3 $output -o $output # optimize
}

# Exports
## NVM
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"  # This loads nvm
[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"  # This loads nvm bash_completion

## Android
export ANDROID_HOME=/usr/local/share/android-sdk
export PATH=$ANDROID_HOME/tools:$PATH
export PATH=$ANDROID_HOME/platform-tools:$PATH
export PATH=$ANDROID_HOME/build-tools/19.1.0:$PATH

## Binaries and other exports
export PATH="$HOME/.fastlane/bin:$PATH"
export PATH=$PATH:$HOME/go/bin
export PATH="$HOME/.yarn/bin:$HOME/.config/yarn/global/node_modules/.bin:$PATH"