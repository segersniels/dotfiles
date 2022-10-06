FILES?=vimrc gitconfig hyper.js

update-all: $(patsubst %, update-%, $(FILES))
update-%:
	rsync ~/.$* .$*
update:
	@$(foreach file, $(FILES), make update-$(file);)