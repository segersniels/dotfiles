FILES?=gitconfig gitignore zshrc vimrc

backup-all: $(patsubst %, backup-%, $(FILES))

backup-%:
	@cp -Rv ~/.$* .$*

backup-nvim:
	@mkdir -p .nvim
	@cp -Rv ~/.config/nvim/* .nvim
	@rm -rf .nvim/pack

backup-ghostty:
	@mkdir -p .ghostty
	@cp -Rv ~/.config/ghostty/* .ghostty
	@cp ~/Library/Application\ Support/com.mitchellh.ghostty/config	.ghostty/config

backup-claude:
	@mkdir -p .claude/commands .claude/agents
	@cp -v ~/.claude/CLAUDE.md .claude/CLAUDE.md
	@cp -v ~/.claude/settings.json .claude/settings.json
	@cp -Rv ~/.claude/commands/* .claude/commands
	@cp -Rv ~/.claude/agents/* .claude/agents

backup-codex:
	@mkdir -p .codex/skills .codex/rules .codex/prompts
	@cp -v ~/.codex/config.toml .codex/config.toml
	@cp -v ~/.codex/AGENTS.md .codex/AGENTS.md
	@cp -Rv ~/.codex/skills/* .codex/skills
	@cp -Rv ~/.codex/rules/* .codex/rules
	@cp -Rv ~/.codex/prompts/* .codex/prompts

backup-opencode:
	@mkdir -p .opencode/commands .opencode/skill
	@cp -v ~/.config/opencode/opencode.jsonc .opencode/opencode.jsonc
	@cp -v ~/.config/opencode/AGENTS.md .opencode/AGENTS.md
	@cp -Rv ~/.config/opencode/commands/* .opencode/commands
	@cp -Rv ~/.config/opencode/skill/* .opencode/skill

backup: backup-nvim backup-ghostty backup-claude backup-codex
	@$(foreach file, $(FILES), make backup-$(file);)

restore-all: $(patsubst %, restore-%, $(FILES))

restore-%:
	@cp -v .$* ~/.$*

restore-nvim:
	@mkdir -p ~/.config/nvim
	@cp -Rv .nvim/* ~/.config/nvim

restore-ghostty:
	@mkdir -p ~/.config/ghostty
	@cp -Rv .ghostty/* ~/.config/ghostty
	@cp .ghostty/config ~/Library/Application\ Support/com.mitchellh.ghostty/config

restore-claude:
	@mkdir -p ~/.claude
	@cp -Rv .claude/* ~/.claude

restore-codex:
	@mkdir -p ~/.codex
	@cp -Rv .codex/* ~/.codex

restore-opencode:
	@mkdir -p ~/.config/opencode
	@cp -Rv .opencode/* ~/.config/opencode

restore-secrets:
	@if [ ! -f ~/.secrets ]; then \
		cp -v .secrets ~/.secrets; \
	else \
		echo "~/.secrets already exists. Skipping."; \
	fi

restore: restore-nvim restore-ghostty restore-secrets restore-claude restore-codex
	@$(foreach file, $(FILES), make restore-$(file);)
