#!/usr/bin/env bash

NODE_VERSION=16
DOTFILES_REPO=https://github.com/segersniels/dotfiles

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
    echo "Git not found. Installing..."
    brew install git
fi

# Clone the repository
echo "Preparing local environment..."
git clone $DOTFILES_REPO &>/dev/null
pushd ./dotfiles

# Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >>${HOME}/.zprofile
eval "$(/opt/homebrew/bin/brew shellenv)"
brew update
brew upgrade
brew bundle
brew cleanup

# Change default shell to zsh
chsh -s /usr/local/bin/zsh

# Setup base environment using Fig
fig login
fig source

# Node
mkdir -p ${HOME}/.nvm
export NVM_DIR="$HOME/.nvm"
[ -s "/opt/homebrew/opt/nvm/nvm.sh" ] && . "/opt/homebrew/opt/nvm/nvm.sh"                                       # This loads nvm
[ -s "/opt/homebrew/opt/nvm/etc/bash_completion.d/nvm" ] && . "/opt/homebrew/opt/nvm/etc/bash_completion.d/nvm" # This loads nvm bash_completion
nvm install $NODE_VERSION
nvm alias default $NODE_VERSION

# Yarn
npm install --global yarn

# Node packages
yarn global add ts-node
yarn global add typescript
yarn global add @segersniels/gitmoji
yarn global add supdock

# Finalize
rsync .vimrc ${HOME}/.vimrc
rsync .gitignore ${HOME}/.gitignore
rsync .gitconfig ${HOME}/.gitconfig
rsync .hyper.js ${HOME}/.hyper.js

# Move back to original directory
popd

# Clean up
rm -rf ./dotfiles
