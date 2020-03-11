#!/usr/bin/env bash

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
/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
brew update
brew upgrade
brew install git
brew install tig
brew install gh
brew install zsh
brew install zsh-completions
brew install grep
brew install jq
brew install curl
brew install wget
brew install yarn
brew install node
brew install watchman
brew install docker-compose
brew install cask
brew install go
brew install coreutils
brew install findutils
brew install autosuggestions
brew install zsh-syntax-highlighting
brew install thefuck # CLI failed command correction
brew install ncdu # Interactive diskspace overview
brew install ffmpeg
brew install gifsicle
brew cleanup

# Cask
brew tap caskroom/versions
brew cask install 1password
brew cask install spectacle
brew cask install visual-studio-code
brew cask install sequel-pro
brew cask install docker
brew cask install google-chrome
brew cask install spotify
brew cask install dropbox
brew cask install vlc
brew cask install slack
brew cask install discord
brew cask install java8
brew cask install android-sdk
brew cask install android-platform-tools
brew cask install android-studio
brew cask install androidtool
brew cask install caskroom/fonts/font-open-sans
brew cask install caskroom/fonts/font-roboto
brew cask install caskroom/fonts/font-source-code-pro
brew cask install font-roboto-mono-for-powerline
brew cask install hyper
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
yarn global add git+https://git@github.com/segersniels/gitmoji-cli.git
yarn global add supdock
yarn global add now

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
code --install-extension mikestead.dotenv
code --install-extension vsmobile.vscode-react-native
code --install-extension ms-vscode.vscode-typescript-tslint-plugin
code --install-extension daylerees.rainglow

# ZSH
sh -c "$(curl -fsSL https://raw.githubusercontent.com/robbyrussell/oh-my-zsh/master/tools/install.sh)"
git clone https://github.com/zsh-users/zsh-autosuggestions ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-autosuggestions

# Git
git config --global pull.rebase true

# Finalize
cp .vscode-settings.json ${HOME}/Library/Application\ Support/Code/User/settings.json
cp .zshrc ${HOME}/.zshrc
cp .vimrc ${HOME}/.vimrc
mkdir -p ${HOME}/.hyper_plugins && cp .hyper-sync-settings.json ${HOME}/.hyper_plugins/.hyper-sync-settings.json