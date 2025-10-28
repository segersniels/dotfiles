-- Primarily used to tell a specific LSP how to behave
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
			eslint = function()
				Snacks.util.lsp.on({ name = "eslint" }, function(_, client)
					client.server_capabilities.documentFormattingProvider = true
				end)
			end,
		},
	},
}
