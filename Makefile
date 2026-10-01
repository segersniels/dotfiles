FILES?=gitconfig gitignore zshrc zprofile vimrc

backup-all: $(patsubst %, backup-%, $(FILES))

backup-%:
	@cp -Rv ~/.$* .$*

backup-nvim:
	@rm -rf .nvim
	@rsync -av --exclude='pack' ~/.config/nvim/ .nvim/

backup-ghostty:
	@rm -rf .ghostty
	@rsync -av ~/.config/ghostty/ .ghostty/

backup-cmux: backup-ghostty
	@rm -rf .cmux
	@mkdir -p .cmux
	@scripts/export-cmux-config > .cmux/cmux.json

backup-agents:
	@rm -rf .agents
	@mkdir -p .agents
	@rsync -av --exclude='target/' --exclude='.git/' --exclude='__pycache__/' --exclude='*.pyc' --exclude='.pytest_cache/' --exclude='.ruff_cache/' --exclude='.trash/' ~/.agents/ .agents/

backup-codex: backup-agents
	@rm -rf .codex
	@mkdir -p .codex
	@rsync -av --exclude='.system/' ~/.codex/skills/ .codex/skills/
	@rsync -av ~/.codex/rules/ .codex/rules/
	@rsync -av ~/.codex/agents/ .codex/agents/
	@rsync -av ~/.codex/hooks/ .codex/hooks/
	@rsync -av --exclude='target/' --exclude='.git/' --exclude='__pycache__/' --exclude='*.pyc' ~/.codex/clis/ .codex/clis/

backup-claude: backup-agents
	@mkdir -p .claude
	@rsync -av ~/.claude/settings.json .claude/
	@rsync -av --delete ~/.claude/agents/ .claude/agents/
	@rsync -av --delete ~/.claude/hooks/ .claude/hooks/

backup-mise:
	@mkdir -p .mise-global
	@rsync -av ~/.config/mise/config.toml .mise-global/

backup-starship:
	@rsync -av ~/.config/starship.toml .starship.toml

backup-cursor:
	@rm -rf .cursor
	@mkdir -p .cursor/user/snippets
	@rsync -av ~/Library/Application\ Support/Cursor/User/settings.json .cursor/user/
	@rsync -av ~/Library/Application\ Support/Cursor/User/keybindings.json .cursor/user/
	@rsync -av ~/Library/Application\ Support/Cursor/User/snippets/ .cursor/user/snippets/
	@rsync -av ~/.cursor/settings.json .cursor/
	@rsync -av ~/.cursor/cli-config.json .cursor/

backup: backup-nvim backup-cmux backup-codex backup-claude backup-cursor backup-mise backup-starship
	@$(foreach file, $(FILES), make backup-$(file);)

restore-all: $(patsubst %, restore-%, $(FILES))

restore-%:
	@cp -v .$* ~/.$*

restore-nvim:
	@rsync -av .nvim/ ~/.config/nvim/

restore-ghostty:
	@rsync -av .ghostty/ ~/.config/ghostty/

restore-cmux: restore-ghostty
	@mkdir -p ~/.config/cmux
	@rsync -av .cmux/cmux.json ~/.config/cmux/

restore-agents:
	@mkdir -p ~/.agents ~/.config/opencode
	@rsync -av .agents/ ~/.agents/

restore-codex: restore-agents
	@mkdir -p ~/.codex
	@rsync -av --exclude='skills/.system/' .codex/ ~/.codex/
	@ln -sfn ~/.agents/AGENTS.md ~/.codex/AGENTS.md

restore-claude: restore-agents
	@mkdir -p ~/.claude
	@rsync -av .claude/settings.json ~/.claude/
	@rsync -av .claude/agents/ ~/.claude/agents/
	@rsync -av .claude/hooks/ ~/.claude/hooks/
	@ln -sfn ~/.agents/AGENTS.md ~/.claude/CLAUDE.md
	@ln -sfn ~/.agents/skills ~/.claude/skills

restore-mise:
	@mkdir -p ~/.config/mise
	@rsync -av .mise-global/config.toml ~/.config/mise/

restore-starship:
	@mkdir -p ~/.config
	@rsync -av .starship.toml ~/.config/starship.toml

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

restore: restore-zshrc restore-nvim restore-cmux restore-secrets restore-codex restore-claude restore-cursor restore-mise restore-starship
	@$(foreach file, $(FILES), make restore-$(file);)
