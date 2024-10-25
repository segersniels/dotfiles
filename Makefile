FILES?=gitconfig gitignore zshrc vimrc

backup-all: $(patsubst %, backup-%, $(FILES))

backup-%:
	@cp -Rv ~/.$* .$*

backup-warp:
	@mkdir -p .warp
	@cp -Rv ~/.warp/* .warp

backup-nvim:
	@mkdir -p .nvim
	@cp -Rv ~/.config/nvim/* .nvim
	@rm -rf .nvim/pack

backup: backup-warp backup-nvim
	@$(foreach file, $(FILES), make backup-$(file);)

restore-all: $(patsubst %, restore-%, $(FILES))

restore-%:
	@cp -v .$* ~/.$*

restore-warp:
	@mkdir -p ~/.warp
	@cp -Rv .warp/* ~/.warp

restore-nvim:
	@mkdir -p ~/.config/nvim
	@cp -Rv .nvim/* ~/.config/nvim

restore-secrets:
	@if [ ! -f ~/.secrets ]; then \
		cp -v .secrets ~/.secrets; \
	else \
		echo "~/.secrets already exists. Skipping."; \
	fi

restore: restore-warp restore-nvim restore-secrets
	@$(foreach file, $(FILES), make restore-$(file);)
