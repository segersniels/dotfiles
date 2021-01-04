update:
	rsync ~/Library/Application\ Support/Code/User/settings.json .vscode-settings.json 
	rsync ~/.zshrc .zshrc 
	rsync ~/.vimrc .vimrc 
	rsync ~/.hyper_plugins/.hyper-sync-settings.json .hyper-sync-settings.json
	rsync ~/.gitconfig .gitconfig