---@param bufnr integer
---@param ... string
---@return string
local function first(bufnr, ...)
	local conform = require("conform")
	for i = 1, select("#", ...) do
		local formatter = select(i, ...)
		if conform.get_formatter_info(formatter, bufnr).available then
			return formatter
		end
	end
	return select(1, ...)
end

return {
	"stevearc/conform.nvim",
	opts = {
		log_level = vim.log.levels.DEBUG,
		formatters_by_ft = {
			javascript = function(bufnr)
				return { first(bufnr, "prettierd", "prettier"), "injected" }
			end,
			javascriptreact = function(bufnr)
				return { first(bufnr, "prettierd", "prettier"), "injected" }
			end,
			typescript = function(bufnr)
				return { first(bufnr, "prettierd", "prettier"), "injected" }
			end,
			typescriptreact = function(bufnr)
				return { first(bufnr, "prettierd", "prettier"), "injected" }
			end,
		},
	},
}
