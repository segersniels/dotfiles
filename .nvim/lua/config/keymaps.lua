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

-- Copy relative path with line or range to system clipboard
vim.keymap.set({ "n", "v" }, "<leader>cP", function()
	local path = vim.api.nvim_buf_get_name(0)
	if path == "" then
		return
	end

	local relative_path = vim.fn.fnamemodify(path, ":.")
	local mode = vim.fn.mode()
	local line_info

	if mode == "v" or mode == "V" or mode == "\22" then
		local start_line = vim.fn.getpos("v")[2]
		local end_line = vim.fn.getpos(".")[2]

		if start_line > end_line then
			start_line, end_line = end_line, start_line
		end

		if start_line == end_line then
			line_info = tostring(start_line)
		else
			line_info = string.format("%d-%d", start_line, end_line)
		end
	else
		line_info = tostring(vim.api.nvim_win_get_cursor(0)[1])
	end

	vim.fn.setreg("+", string.format("%s:%s", relative_path, line_info))
end, { desc = "Copy relative path with lines" })

-- Surround selection with backticks
vim.keymap.set("v", "`", "c``<Esc>P", { desc = "Surround selection with backticks" })
