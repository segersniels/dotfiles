FILES?=gitconfig gitignore zshrc vimrc

backup-all: $(patsubst %, backup-%, $(FILES))

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

restore-secrets:
	@if [ ! -f ~/.secrets ]; then \
		cp -v .secrets ~/.secrets; \
	else \
		echo "~/.secrets already exists. Skipping."; \
	fi

restore: restore-warp restore-secrets
	@$(foreach file, $(FILES), make restore-$(file);)
