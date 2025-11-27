return {
	"folke/snacks.nvim",
	priority = 1000,
	lazy = false,
	opts = {
		dashboard = {
			sections = {
				{ section = "header" },
				{ section = "keys", padding = 2 },
				{ section = "startup" },
			},
		},
		scroll = { enabled = true },
		picker = {
			layout = {
				preset = "default", -- "default" for floating, "ivy" for bottom embedded
			},
			matcher = {
				fuzzy = true,
			},
			sources = {
				files = { hidden = true, ignored = false, regex = false },
				grep = { hidden = true, ignored = false, regex = false },
				explorer = { hidden = true, ignored = true, regex = false },
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
