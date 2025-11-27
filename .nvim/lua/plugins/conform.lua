return {
	"stevearc/conform.nvim",
	opts = function(_, opts)
		opts.formatters_by_ft = opts.formatters_by_ft or {}

		local js_ft = {
			"javascript",
			"javascriptreact",
			"typescript",
			"typescriptreact",
			"vue",
			"svelte",
		}

		for _, ft in ipairs(js_ft) do
			-- Prefer ESLint LSP formatting (matches VS Code). No extra formatter entries to avoid conflicts/errors.
			opts.formatters_by_ft[ft] = {}
		end

		return opts
	end,
}
