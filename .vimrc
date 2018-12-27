syntax on
set tabstop=2
set shiftwidth=2
set softtabstop=2
set expandtab

filetype on
filetype plugin on
filetype indent on

autocmd FileType make setlocal shiftwidth=4 softtabstop=4 tabstop=4 noexpandtab
autocmd Filetype javascript setlocal shiftwidth=4 softtabstop=4 tabstop=4 noexpandtab
autocmd BufRead,BufNewFile *.conf setlocal shiftwidth=4 softtabstop=4 tabstop=4 noexpandtab
autocmd FileType json setlocal shiftwidth=4 softtabstop=4 tabstop=4 noexpandtab

set noswapfile
