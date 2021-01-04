FILES?=zshrc vimrc gitconfig

update: update-all
	rsync ~/Library/Application\ Support/Code/User/settings.json .vscode-settings.json 
	rsync ~/.hyper_plugins/.hyper-sync-settings.json .hyper-sync-settings.json

update-all: $(patsubst %, update-%, $(FILES))
update-%:
	rsync ~/.$* .$*