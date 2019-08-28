#!/usr/bin/env bash
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
