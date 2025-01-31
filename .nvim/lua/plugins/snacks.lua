return {
	"folke/snacks.nvim",
	opts = {
		picker = {
			sources = {
				files = { hidden = true, ignored = true },
				grep = { hidden = true, ignored = false },
				explorer = { hidden = true, ignored = true },
			},
			win = {
				input = {
					keys = {
						["<Esc>"] = false,
					},
				},
				list = {
					keys = {
						["<Esc>"] = false,
					},
				},
				preview = {
					keys = {
						["<Esc>"] = false,
					},
				},
			},
		},
	},
	keys = {
		{
			"<leader><space>",
			function()
				local instance = Snacks.picker.get({ source = "explorer" })[1]
				if instance then
					instance.input.win:focus()
				else
					Snacks.explorer({ focus = "input" })
				end
			end,
			desc = "Find files",
		},
	},
}
