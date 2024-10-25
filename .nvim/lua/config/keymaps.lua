-- Default keymaps that are always set: https://github.com/LazyVim/LazyVim/blob/main/lua/lazyvim/config/keymaps.lua

-- Paste without yanking - paste over selection while preserving clipboard content
vim.keymap.set("x", "<leader>p", [["_dP]], { desc = "Paste without yanking" })

-- Copy to system clipboard in normal and visual mode
vim.keymap.set({ "n", "v" }, "<leader>y", [["+y]], { desc = "Copy to system clipboard" })

-- Copy whole line to system clipboard in normal mode
vim.keymap.set("n", "<leader>Y", [["+Y]], { desc = "Copy whole line to system clipboard" })

-- Insert console.log with cursor in position
vim.keymap.set("n", "<leader>cL", 'iconsole.log("------>", );<Esc>hi', { desc = "Insert a new log" })

-- Select word and create console.log below with the word
vim.keymap.set(
	"v",
	"<leader>cL",
	'yoconsole.log("------>", { <Esc>p<S-a> });<Esc>',
	{ desc = "Log the selected variable" }
)
