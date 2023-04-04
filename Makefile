FILES?=vimrc gitconfig gitignore hyper.js

backup-all: $(patsubst %, restore-%, $(FILES))
backup-%:
	@cp -Rv ~/.$* .$*
backup-warp:
	@mkdir -p .warp
	@cp -Rv ~/.warp/* .warp
backup: backup-warp
	@$(foreach file, $(FILES), make backup-$(file);)

restore-all: $(patsubst %, restore-%, $(FILES))
restore-%:
	@cp -v .$* ~/.$*
restore-warp:
	@mkdir -p ~/.warp
	@cp -Rv .warp/* ~/.warp
restore: restore-warp
	@$(foreach file, $(FILES), make restore-$(file);)