return {
	{
		"hrsh7th/nvim-cmp",
		keys = {
			-- Disable tab keybind so other AI auto completion can use it
			{ "<tab>", false, mode = { "i", "s" } },
			{ "<s-tab>", false, mode = { "i", "s" } },
		},
	},
}
