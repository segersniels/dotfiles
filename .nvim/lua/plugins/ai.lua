return {
	{
		"yetone/avante.nvim",
		event = "VeryLazy",
		lazy = false,
		version = false,
		opts = {
			provider = "copilot",
			auto_suggestions_provider = "copilot",
			claude = {
				model = "claude-3-5-sonnet-latest",
			},
			copilot = {
				model = "claude-3.5-sonnet",
			},
			behaviour = {
				auto_suggestions = false,
				auto_set_highlight_group = true,
				auto_set_keymaps = true,
				auto_apply_diff_after_generation = false,
				support_paste_from_clipboard = false,
				minimize_diff = true, -- Whether to remove unchanged lines when applying a code block
			},
			vendors = {
				deepseek = {
					__inherited_from = "openai",
					api_key_name = "DEEPSEEK_API_KEY",
					endpoint = "https://api.deepseek.com",
					model = "deepseek-chat",
					timeout = 30000,
					temperature = 0,
					max_tokens = 4096,
				},
			},
			suggestion = {
				debounce = 600,
				throttle = 600,
			},
		},
		build = "make",
		dependencies = {
			"stevearc/dressing.nvim",
			"nvim-lua/plenary.nvim",
			"MunifTanjim/nui.nvim",
			"nvim-tree/nvim-web-devicons",
			"hrsh7th/nvim-cmp", -- autocompletion for avante commands and mentions
			"ibhagwan/fzf-lua", -- for file_selector provider fzf
			"zbirenbaum/copilot.lua", -- for providers='copilot'
		},
	},
}
