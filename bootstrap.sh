#!/bin/bash

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

# Fix fonts on Mojave
defaults write -g CGFontRenderingFontSmoothingDisabled -bool FALSE

# Disable smart quotes as they’re annoying when typing code
defaults write NSGlobalDomain NSAutomaticQuoteSubstitutionEnabled -bool false

# Disable smart dashes as they’re annoying when typing code
defaults write NSGlobalDomain NSAutomaticDashSubstitutionEnabled -bool false

# Homebrew
cd /opt && mkdir homebrew && curl -L https://github.com/Homebrew/brew/tarball/master | tar xz --strip 1 -C homebrew
brew update
brew upgrade
brew bundle
brew cleanup

# Node packages
yarn global add yarn
yarn global add react-devtools
yarn global add react-native-cli
yarn global add flow-bin
yarn global add wml
yarn global add webpack
yarn global add ts-node
yarn global add typescript
yarn global add @segersniels/gitmoji
yarn global add supdock
yarn global add vercel

# Gems
gem install bundler

# Code packages
code --install-extension dbaeumer.vscode-eslint
code --install-extension eamodio.gitlens
code --install-extension editorconfig.editorconfig
code --install-extension flowtype.flow-for-vscode
code --install-extension naumovs.color-highlight
code --install-extension peterjausovec.vscode-docker
code --install-extension esbenp.prettier-vscode
code --install-extension zignd.html-css-class-completion
code --install-extension mikestead.dotenv
code --install-extension whatwedo.twig
code --install-extension ricard.postcss
code --install-extension mechatroner.rainbow-csv
code --install-extension vsmobile.vscode-react-native
code --install-extension ms-vscode.vscode-typescript-tslint-plugin
code --install-extension daylerees.rainglow

# ZSH
sh -c "$(curl -fsSL https://raw.githubusercontent.com/robbyrussell/oh-my-zsh/master/tools/install.sh)"
git clone https://github.com/zsh-users/zsh-autosuggestions ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-autosuggestions

# Finalize
mkdir -p ${HOME}/.hyper_plugins && cp .hyper-sync-settings.json ${HOME}/.hyper_plugins/.hyper-sync-settings.json
rsync .vscode-settings.json ${HOME}/Library/Application\ Support/Code/User/settings.json
rsync .zshrc ${HOME}/.zshrc
rsync .vimrc ${HOME}/.vimrc
rsync .gitignore ${HOME}/.gitignore
rsync .gitconfig ${HOME}/.gitconfig