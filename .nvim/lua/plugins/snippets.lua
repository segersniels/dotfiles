return {
	{
		"saghen/blink.cmp",
		version = "*",
		dependencies = { "L3MON4D3/LuaSnip", version = "v2.*" },
		opts = {
			snippets = { preset = "luasnip" },
			sources = {
				default = { "lsp", "path", "snippets", "buffer" },
			},
		},
	},
	{
		"L3MON4D3/LuaSnip",
		opts = function()
			local ls = require("luasnip")
			local s = ls.snippet
			local t = ls.text_node
			local i = ls.insert_node
			for _, ft in ipairs({ "javascript", "typescript", "javascriptreact", "typescriptreact" }) do
				ls.add_snippets(ft, {
					s("clog", {
						t('console.log("------>", '),
						i(1),
						t(")"),
					}),
				})
				ls.add_snippets(ft, {
					s("jlog", {
						t('console.log("------>", JSON.stringify('),
						i(1),
						t(", null, 2))"),
					}),
				})
			end
		end,
	},
}
