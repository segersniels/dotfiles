#!/usr/bin/env bash

NODE_VERSION=16
DOTFILES_REPO=https://github.com/segersniels/dotfiles
ZSHRC_FILE=$HOME/.zshrc

function log {
    echo "[INFO] $1"
}

# Ask for the administrator password upfront.
sudo -v

# Keep-alive: update existing `sudo` time stamp until the script has finished.
while true; do
    sudo -n true
    sleep 60
    kill -0 "$$" || exit
done 2>/dev/null &

# Allow apps from anywhere
sudo spctl --master-disable

# Disable guest user
sudo defaults write /Library/Preferences/com.apple.loginwindow GuestEnabled -bool false

# Disable smart quotes as they’re annoying when typing code
defaults write NSGlobalDomain NSAutomaticQuoteSubstitutionEnabled -bool false

# Disable smart dashes as they’re annoying when typing code
defaults write NSGlobalDomain NSAutomaticDashSubstitutionEnabled -bool false

# Install git if not available
if git ! --version &>/dev/null; then
    log "Git not found. Installing..."
    brew install git
fi

# Clone the repository
log "Preparing local environment..."
git clone $DOTFILES_REPO &>/dev/null
pushd ./dotfiles

# Homebrew
log "Installing Homebrew..."
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
brew update
brew upgrade
brew bundle
brew cleanup

# ZSH
log "Updating default shell to ZSH..."
chsh -s $(which zsh)

# Fig
log "Installing Fig..."
fig login
touch $ZSHRC_FILE # Create the .zshrc file so NVM can install with it being present

# NVM
log "Preparing node v${NODE_VERSION}..."
mkdir -p ${HOME}/.nvm
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.1/install.sh | bash
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"
nvm install $NODE_VERSION
nvm alias default $NODE_VERSION

# Node
log "Installing node packages..."
npm install --global yarn
yarn global add -s ts-node
yarn global add -s typescript
yarn global add -s @segersniels/gitmoji
yarn global add -s supdock

# Finalize
log "Syncing config files..."
rsync .vimrc ${HOME}/.vimrc
rsync .gitignore ${HOME}/.gitignore
rsync .gitconfig ${HOME}/.gitconfig
rsync .hyper.js ${HOME}/.hyper.js

# Move back to original directory
log "Moving back to original directory and cleaning up..."
popd
rm -rf ./dotfiles

# Finishing up
fig install --dotfiles
fig source
log "To finish the setup please run 'source $ZSHRC_FILE'! If something went wrong check if Fig sourced the dotfiles correctly or run 'fig source' and debug."
