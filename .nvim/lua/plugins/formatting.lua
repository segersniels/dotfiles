-- We rely on prettierd to format our javascript and typescript files because
-- relying on regular prettier was very slow. We also use conform.nvim to
-- ensure that prettierd is used to format our files before trying prettier.
--
-- TODO: At one point we probably just want to use prettier and drop the entire
-- prettierd thing.
return {
	{
		"williamboman/mason.nvim",
		opts = {
			ensure_installed = { "prettierd", "prettier" },
		},
	},
	{
		"stevearc/conform.nvim",
		opts = {
			formatters_by_ft = {
				javascript = { "prettierd", "prettier", stop_after_first = true },
				typescript = { "prettierd", "prettier", stop_after_first = true },
				typescriptreact = { "prettierd", "prettier", stop_after_first = true },
				javascriptreact = { "prettierd", "prettier", stop_after_first = true },
			},
		},
	},
}
