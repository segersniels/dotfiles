FILES?=gitconfig gitignore zshrc

backup-all: $(patsubst %, backup-%, $(FILES))

backup-%:
	@cp -Rv ~/.$* .$*
backup-warp:
	@mkdir -p .warp
	@cp -Rv ~/.warp/* .warp
backup-nvim:
	@mkdir -p .config/nvim
	@cp ~/.config/nvim/init.vim .config/nvim/
backup: backup-warp backup-nvim
	@$(foreach file, $(FILES), make backup-$(file);)

restore-all: $(patsubst %, restore-%, $(FILES))
restore-%:
	@cp -v .$* ~/.$*
restore-warp:
	@mkdir -p ~/.warp
	@cp -Rv .warp/* ~/.warp
restore-nvim:
	@mkdir -p ~/.config
	@cp -Rv .config/nvim ~/.config/nvim
restore: restore-warp restore-nvim
	@$(foreach file, $(FILES), make restore-$(file);)
