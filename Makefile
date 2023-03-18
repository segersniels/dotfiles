FILES?=vimrc gitconfig gitignore hyper.js

backup-all: $(patsubst %, restore-%, $(FILES))
backup-%:
	@cp -Rv ~/.$* .$*
backup-zed:
	@mkdir -p .config
	@cp -Rv ~/.config/zed .config
backup: backup-zed
	@$(foreach file, $(FILES), make backup-$(file);)

restore-all: $(patsubst %, restore-%, $(FILES))
restore-%:
	@cp -v .$* ~/.$*
restore-zed:
	@mkdir -p ~/.config
	@cp -Rv .config/zed ~/.config
restore: restore-zed
	@$(foreach file, $(FILES), make restore-$(file);)
