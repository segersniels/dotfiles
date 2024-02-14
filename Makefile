FILES?=vimrc gitconfig gitignore

backup-all: $(patsubst %, restore-%, $(FILES))
backup-%:
	@cp -Rv ~/.$* .$*
backup-warp:
	@mkdir -p .warp
	@cp -Rv ~/.warp/* .warp
backup-zed:
	@mkdir -p .config/zed
	@cp ~/.config/zed/*.json .config/zed/
	@rm -rf .config/zed/themes && cp -R ~/.config/zed/themes .config/zed/themes
backup: backup-warp
	@$(foreach file, $(FILES), make backup-$(file);)

restore-all: $(patsubst %, restore-%, $(FILES))
restore-%:
	@cp -v .$* ~/.$*
restore-warp:
	@mkdir -p ~/.warp
	@cp -Rv .warp/* ~/.warp
restore-zed:
	@mkdir -p ~/.config
	@cp -Rv .config/* ~/.config
restore: restore-warp restore-zed
	@$(foreach file, $(FILES), make restore-$(file);)
