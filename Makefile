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
	@rsync -av --exclude='.system/' ~/.codex/skills/ .codex/skills/
	@rsync -av ~/.codex/rules/ .codex/rules/
	@rsync -av ~/.codex/agents/ .codex/agents/

backup-opencode:
	@rm -rf .opencode
	@rsync -av ~/.config/opencode/opencode.jsonc .opencode/
	@rsync -av ~/.config/opencode/AGENTS.md .opencode/
	@rsync -av ~/.config/opencode/commands/ .opencode/commands/
	@rsync -av ~/.config/opencode/skill/ .opencode/skill/

backup-cursor:
	@rm -rf .cursor
	@mkdir -p .cursor/user/snippets
	@rsync -av ~/Library/Application\ Support/Cursor/User/settings.json .cursor/user/
	@rsync -av ~/Library/Application\ Support/Cursor/User/keybindings.json .cursor/user/
	@rsync -av ~/Library/Application\ Support/Cursor/User/snippets/ .cursor/user/snippets/
	@rsync -av ~/.cursor/settings.json .cursor/
	@rsync -av ~/.cursor/cli-config.json .cursor/

backup: backup-nvim backup-ghostty backup-claude backup-codex backup-cursor
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
	@rsync -av --exclude='skills/.system/' .codex/ ~/.codex/

restore-opencode:
	@rsync -av .opencode/ ~/.config/opencode/

restore-cursor:
	@mkdir -p ~/Library/Application\ Support/Cursor/User/snippets
	@mkdir -p ~/.cursor
	@rsync -av .cursor/user/settings.json ~/Library/Application\ Support/Cursor/User/
	@rsync -av .cursor/user/keybindings.json ~/Library/Application\ Support/Cursor/User/
	@rsync -av .cursor/user/snippets/ ~/Library/Application\ Support/Cursor/User/snippets/
	@rsync -av .cursor/settings.json ~/.cursor/
	@rsync -av .cursor/cli-config.json ~/.cursor/

restore-secrets:
	@if [ ! -f ~/.secrets ]; then \
		cp -v .secrets ~/.secrets; \
	else \
		echo "~/.secrets already exists. Skipping."; \
	fi

restore: restore-nvim restore-ghostty restore-secrets restore-claude restore-codex restore-cursor
	@$(foreach file, $(FILES), make restore-$(file);)
