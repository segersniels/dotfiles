-- Default options that are always set: https://github.com/LazyVim/LazyVim/blob/main/lua/lazyvim/config/options.lua

-- Disable relative line numbers
vim.opt.relativenumber = false

-- Recommended by Avante to ensure that there's always a single, global status line visible at the bottom of the Neovim interface
vim.opt.laststatus = 3

-- Enable mouse support for side button navigation and hover
vim.opt.mouse = "a"
vim.opt.mousehide = false

-- Disable CMP AI-based code completion suggestions so Tab works
vim.g.ai_cmp = false

-- Disable list characters (e.g., showing tabs and trailing spaces)
vim.opt.list = false
