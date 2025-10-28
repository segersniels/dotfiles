return {
	"folke/snacks.nvim",
	priority = 1000,
	opts = {
		picker = {
			sources = {
				files = { hidden = true, ignored = true },
				grep = { hidden = true, ignored = true },
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
				local pickers = Snacks.picker.get({ source = "explorer" })
				if pickers and #pickers > 0 then
					pickers[1].input.win:focus()
				else
					Snacks.explorer({ focus = "input" })
				end
			end,
			desc = "Find files",
		},
	},
}
