#!/usr/bin/env bash
cp .vscode-settings.json ${HOME}/Library/Application\ Support/Code/User/settings.json
cp .zshrc ${HOME}/.zshrc
cp .vimrc ${HOME}/.vimrc
mkdir -p ${HOME}/.hyper_plugins && cp .hyper-sync-settings.json ${HOME}/.hyper_plugins/.hyper-sync-settings.json