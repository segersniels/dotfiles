#!/usr/bin/env bash

NODE_VERSION=16
DOTFILES_REPO=https://github.com/segersniels/dotfiles
ZSHRC_FILE=$HOME/.zshrc

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

# Install Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
(echo; echo 'eval "$(/opt/homebrew/bin/brew shellenv)"') >> ${HOME}/.zprofile
eval "$(/opt/homebrew/bin/brew shellenv)"

# Install git if not available
if git ! --version &>/dev/null; then
    brew install git
fi

# Clone the repository
git clone $DOTFILES_REPO &>/dev/null
pushd ./dotfiles

# Update and install brew packages
brew update
brew upgrade
brew bundle
brew cleanup

# Install App store apps
mas install 441258766 # Magnet

# ZSH
chsh -s $(which zsh)

# Fig
fig login
touch $ZSHRC_FILE # Create the .zshrc file so NVM can install with it being present

# NVM
mkdir -p ${HOME}/.nvm
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.1/install.sh | bash
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"
nvm install $NODE_VERSION
nvm alias default $NODE_VERSION

# Finalize
make restore

# Move back to original directory
popd
rm -rf ./dotfiles

# Node
npm install --global --silent gitmoji-cli
npm install --global --silent supdock
npm install --global --silent ts-node
npm install --global --silent typescript
npm install --global --silent turbo
npm install --global --silent yarn
npm install --global --silent pnpm

# Finishing up
fig install --dotfiles
fig source
echo "To finish the setup please run 'source $ZSHRC_FILE'! If something went wrong check if Fig sourced the dotfiles correctly or run 'fig source' and debug."
