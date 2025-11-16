return {
	"folke/snacks.nvim",
	priority = 1000,
	lazy = false,
	opts = {
		scroll = { enabled = true },
		picker = {
			sources = {
				files = { hidden = true, ignored = false },
				grep = { hidden = true, ignored = false },
				explorer = { hidden = true, ignored = false },
			},
			win = {
				input = {
					keys = {
						["<Esc>"] = false,
						["<c-s>"] = false, -- Disable ctrl+s in input window
					},
				},
				list = {
					keys = {
						["<Esc>"] = false,
						["<c-s>"] = false, -- Disable ctrl+s in list window
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
