-- Default keymaps that are always set: https://github.com/LazyVim/LazyVim/blob/main/lua/lazyvim/config/keymaps.lua

-- Paste without yanking - paste over selection while preserving clipboard content
vim.keymap.set("x", "<leader>p", [["_dP]], { desc = "Paste without yanking" })

-- Copy to system clipboard in normal and visual mode
vim.keymap.set({ "n", "v" }, "<leader>y", [["+y]], { desc = "Copy to system clipboard" })

-- Copy whole line to system clipboard in normal mode
vim.keymap.set("n", "<leader>Y", [["+Y]], { desc = "Copy whole line to system clipboard" })

-- Insert console.log with cursor in position
vim.keymap.set("n", "<leader>cL", 'iconsole.log("------>", );<Esc>hi', { desc = "Insert a new log" })

-- Insert JSON.stringify console.log with cursor in position
vim.keymap.set(
	"n",
	"<leader>cJ",
	'iconsole.log("------>", JSON.stringify( , null, 2));<Esc>12hi',
	{ desc = "Insert a new JSON log" }
)

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
