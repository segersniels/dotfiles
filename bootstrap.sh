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
brew install zsh
brew install zsh-completions
brew install grep
brew install jq
brew install curl
brew install wget
brew install node
brew install watchman
brew install docker-compose
brew install cask
brew install go
brew install coreutils
brew install findutils
brew cleanup

# Cask
brew tap caskroom/versions
brew cask install 1password
brew cask install spectacle
brew cask install rightzoom
brew cask install visual-studio-code
brew cask install sequel-pro
brew cask install iterm2
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
brew cleanup

# Node packages
npm install -g yarn
npm install -g react-devtools
npm install -g react-native-cli
npm install -g flow-bin
npm install -g wml
npm install -g webpack
npm install -g ts-node
npm install -g typescript
npm install -g pure-prompt

# Gems
gem install bundler

# Code packages
code --install-extension dbaeumer.vscode-eslint
code --install-extension dracula-theme.theme-dracula
code --install-extension eamodio.gitlens
code --install-extension editorconfig.editorconfig
code --install-extension flowtype.flow-for-vscode
code --install-extension naumovs.color-highlight
code --install-extension peterjausovec.vscode-docker
code --install-extension esbenp.prettier-vscode
code --install-extension felixfbecker.php-intellisense
code --install-extension eg2.vscode-npm-script
code --install-extension zignd.html-css-class-completion
code --install-extension ms-python.python
code --install-extension mikestead.dotenv
code --install-extension whatwedo.twig
code --install-extension ricard.postcss
code --install-extension equinusocio.vsc-material-theme
code --install-extension mechatroner.rainbow-csv
code --install-extension christian-kohler.npm-intellisense
code --install-extension mikestead.dotenv
code --install-extension christian-kohler.path-intellisense
code --install-extension vsmobile.vscode-react-native
code --install-extension eg2.tslint

# ZSH
sh -c "$(curl -fsSL https://raw.githubusercontent.com/robbyrussell/oh-my-zsh/master/tools/install.sh)"
git clone https://github.com/zsh-users/zsh-autosuggestions ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-autosuggestions

# Copy dotfiles
cd "$(dirname "${BASH_SOURCE}")"
rsync \
	--exclude ".DS_Store" \
	--exclude ".vscode-settings.json" \
	--exclude ".git/" \
	--exclude "iterm2/" \
	--exclude "bootstrap.sh" \
	--exclude "README.md" \
	-avh --no-perms . ~

cp .vscode-settings.json ${HOME}/Library/Application\ Support/Code/User/settings.json

# Golang packages
go get -u github.com/segersniels/supdock
