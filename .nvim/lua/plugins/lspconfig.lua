return {
	"neovim/nvim-lspconfig",
	opts = {
		servers = {
			eslint = {
				settings = {
					-- Helps eslint find the eslintrc when it's placed in a subfolder instead of the cwd root
					workingDirectory = { mode = "auto" },
				},
			},
			vtsls = {
				settings = {
					typescript = {
						inlayHints = {
							enumMemberValues = { enabled = true },
							functionLikeReturnTypes = { enabled = false },
							parameterNames = { enabled = "all" },
							parameterTypes = { enabled = false },
							propertyDeclarationTypes = { enabled = false },
							variableTypes = { enabled = false },
						},
					},
				},
			},
		},
		setup = {
			vtsls = function()
				vim.api.nvim_create_autocmd("LspAttach", {
					callback = function(args)
						local client = vim.lsp.get_client_by_id(args.data.client_id)

						if not client then
							return
						end

						if client.name == "eslint" then
							-- ESLint LSP is the formatter (mirrors VS Code path).
							client.server_capabilities.documentFormattingProvider = true
						elseif client.name == "vtsls" then
							-- avoid dueling with eslint/prettier
							client.server_capabilities.documentFormattingProvider = false
						end
					end,
				})
			end,
		},
	},
}
