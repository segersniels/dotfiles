#!/usr/bin/env bash

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