FILES?=zshrc vimrc gitconfig hyper.js

update-all: $(patsubst %, update-%, $(FILES))
update-%:
	rsync ~/.$* .$*
update-vscode:
	rsync ~/Library/Application\ Support/Code/User/settings.json .vscode-settings.json 
update: update-vscode
	@$(foreach file, $(FILES), make update-$(file);)