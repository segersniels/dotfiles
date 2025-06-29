#!/usr/bin/env bash

NODE_VERSION=22
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
(
  echo
  echo 'eval "$(/opt/homebrew/bin/brew shellenv)"'
) >>${HOME}/.zprofile
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
sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"

# Finalize
make restore

# Move back to original directory
popd
rm -rf ./dotfiles

# Node
fnm install --lts
npm install -g supdock
npm install -g @segersniels/cmt
npm install -g @anthropic-ai/claude-code

# Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
source "$HOME/.cargo/env"
