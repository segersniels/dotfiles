FILES?=gitconfig gitignore zshrc vimrc

backup-all: $(patsubst %, backup-%, $(FILES))

backup-%:
	@cp -Rv ~/.$* .$*

backup-nvim:
	@rm -rf .nvim
	@rsync -av --exclude='pack' ~/.config/nvim/ .nvim/

backup-ghostty:
	@rm -rf .ghostty
	@rsync -av ~/.config/ghostty/ .ghostty/
	@rsync -av ~/Library/Application\ Support/com.mitchellh.ghostty/config .ghostty/config

backup-claude:
	@rm -rf .claude
	@rsync -av ~/.claude/CLAUDE.md .claude/
	@rsync -av ~/.claude/settings.json .claude/
	@rsync -av ~/.claude/commands/ .claude/commands/
	@rsync -av ~/.claude/agents/ .claude/agents/

backup-codex:
	@rm -rf .codex
	@rsync -av ~/.codex/config.toml .codex/
	@rsync -av ~/.codex/AGENTS.md .codex/
	@rsync -av ~/.codex/skills/ .codex/skills/
	@rsync -av ~/.codex/rules/ .codex/rules/

backup-opencode:
	@rm -rf .opencode
	@rsync -av ~/.config/opencode/opencode.jsonc .opencode/
	@rsync -av ~/.config/opencode/AGENTS.md .opencode/
	@rsync -av ~/.config/opencode/commands/ .opencode/commands/
	@rsync -av ~/.config/opencode/skill/ .opencode/skill/

backup: backup-nvim backup-ghostty backup-claude backup-codex
	@$(foreach file, $(FILES), make backup-$(file);)

restore-all: $(patsubst %, restore-%, $(FILES))

restore-%:
	@cp -v .$* ~/.$*

restore-nvim:
	@rsync -av .nvim/ ~/.config/nvim/

restore-ghostty:
	@rsync -av .ghostty/ ~/.config/ghostty/
	@rsync -av .ghostty/config ~/Library/Application\ Support/com.mitchellh.ghostty/config

restore-claude:
	@rsync -av .claude/ ~/.claude/

restore-codex:
	@rsync -av .codex/ ~/.codex/

restore-opencode:
	@rsync -av .opencode/ ~/.config/opencode/

restore-secrets:
	@if [ ! -f ~/.secrets ]; then \
		cp -v .secrets ~/.secrets; \
	else \
		echo "~/.secrets already exists. Skipping."; \
	fi

restore: restore-nvim restore-ghostty restore-secrets restore-claude restore-codex
	@$(foreach file, $(FILES), make restore-$(file);)
