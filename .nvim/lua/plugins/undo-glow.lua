return {
	"y3owk1n/undo-glow.nvim",
	opts = {
		animation = {
			enabled = true,
			duration = 300,
			fps = 120,
		},
		highlights = {
			undo = {
				hl_color = { bg = "#f9d4d4" },
			},
			redo = {
				hl_color = { bg = "#d4ede4" },
			},
			yank = {
				hl_color = { bg = "#f9ecd4" },
			},
			paste = {
				hl_color = { bg = "#d4e4ed" },
			},
			comment = {
				hl_color = { bg = "#ebe5d8" },
			},
		},
		priority = 2048 * 3,
	},
	keys = {
		{
			"u",
			function()
				require("undo-glow").undo()
			end,
			mode = "n",
			desc = "Undo with highlight",
		},
		{
			"<C-r>",
			function()
				require("undo-glow").redo()
			end,
			mode = "n",
			desc = "Redo with highlight",
			noremap = true,
		},
		{
			"gc",
			function()
				-- This is an implementation to preserve the cursor position
				local pos = vim.fn.getpos(".")
				vim.schedule(function()
					vim.fn.setpos(".", pos)
				end)
				return require("undo-glow").comment()
			end,
			mode = { "n", "x" },
			desc = "Toggle comment with highlight",
			expr = true,
			noremap = true,
		},
		{
			"gc",
			function()
				require("undo-glow").comment_textobject()
			end,
			mode = "o",
			desc = "Comment textobject with highlight",
			noremap = true,
		},
		{
			"gcc",
			function()
				return require("undo-glow").comment_line()
			end,
			mode = "n",
			desc = "Toggle comment line with highlight",
			expr = true,
			noremap = true,
		},
	},
}
