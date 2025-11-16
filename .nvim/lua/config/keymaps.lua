-- Default keymaps that are always set: https://github.com/LazyVim/LazyVim/blob/main/lua/lazyvim/config/keymaps.lua

-- Paste without yanking - paste over selection while preserving clipboard content
vim.keymap.set("x", "<leader>P", [["_dP]], { desc = "Paste without yanking" })

-- Copy to system clipboard in normal and visual mode
vim.keymap.set({ "n", "v" }, "<leader>y", [["+y]], { desc = "Copy to system clipboard" })

-- Select word and create console.log below with the word
vim.keymap.set(
	"v",
	"<leader>cL",
	'yoconsole.log("------>", { <Esc>p<S-a> });<Esc>',
	{ desc = "Log the selected variable" }
)

-- Select word and create JSON.stringify console.log below with the word
vim.keymap.set(
	"v",
	"<leader>cJ",
	'yoconsole.log("------>", JSON.stringify({ <Esc>p<S-a> }, null, 2));<Esc>',
	{ desc = "JSON log the selected variable" }
)

-- Copy relative path of current open buffer
vim.keymap.set("n", "<leader>cp", function()
	local path = vim.api.nvim_buf_get_name(0)
	if path == "" then
		return
	end

	local relative_path = vim.fn.fnamemodify(path, ":.")
	vim.fn.setreg("+", relative_path)
end, { desc = "Copy relative path" })
