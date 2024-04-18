FILES?=gitconfig gitignore zshrc

backup-all: $(patsubst %, restore-%, $(FILES))
backup-%:
	@cp -Rv ~/.$* .$*
backup-warp:
	@mkdir -p .warp
	@cp -Rv ~/.warp/* .warp
backup-zed:
	@mkdir -p .config/zed
	@cp ~/.config/zed/*.json .config/zed/
backup-nvim:
	@mkdir -p .config/nvim
	@cp ~/.config/nvim/init.vim .config/nvim/
backup: backup-warp backup-zed backup-nvim
	@$(foreach file, $(FILES), make backup-$(file);)

restore-all: $(patsubst %, restore-%, $(FILES))
restore-%:
	@cp -v .$* ~/.$*
restore-warp:
	@mkdir -p ~/.warp
	@cp -Rv .warp/* ~/.warp
restore-zed:
	@mkdir -p ~/.config
	@cp -Rv .config/zed ~/.config/zed
restore-nvim:
	@mkdir -p ~/.config
	@cp -Rv .config/nvim ~/.config/nvim
restore: restore-warp restore-zed restore-nvim
	@$(foreach file, $(FILES), make restore-$(file);)
