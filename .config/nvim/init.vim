" Options
set tabstop=2
set shiftwidth=2
set softtabstop=2
set expandtab
set noswapfile
set clipboard=unnamedplus " Enables the clipboard between Vim/Neovim and other applications.
set completeopt=noinsert,menuone,noselect " Modifies the auto-complete menu to behave more like an IDE.
set hidden " Hide unused buffers
set cursorline " Highlights the current line in the editor
set mouse=a " Allow to use the mouse in the editor
set number " Shows the line numbers
set title " Show file title
set wildmenu " Show a more advance menu
set spell " Enable spell check (may need to download language package)
set ttyfast " Speed up scrolling in Vim

syntax on
filetype on
filetype plugin indent on

autocmd FileType make setlocal shiftwidth=4 softtabstop=4 tabstop=4 noexpandtab
autocmd Filetype javascript setlocal shiftwidth=4 softtabstop=4 tabstop=4 noexpandtab
autocmd BufRead,BufNewFile *.conf setlocal shiftwidth=4 softtabstop=4 tabstop=4 noexpandtab
autocmd FileType json setlocal shiftwidth=4 softtabstop=4 tabstop=4 noexpandtab

hi Normal ctermbg=none guibg=none " Disable weird background and respect terminal theme
