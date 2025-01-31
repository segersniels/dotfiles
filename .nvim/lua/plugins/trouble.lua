-- Used to show diagnostics and error reporting of the current file (eg. linting)
return {
	"folke/trouble.nvim",
	cmd = "Trouble",
	opts = {
		auto_preview = true,
		multiline = true,
		modes = {
			diagnostics = { auto_open = true },
		},
	},
}
