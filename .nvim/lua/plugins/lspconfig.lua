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

						if client and client.name == "eslint" then
							client.server_capabilities.documentFormattingProvider = true
						elseif client and client.name == "vtsls" then
							client.server_capabilities.documentFormattingProvider = false
						end
					end,
				})
			end,
			-- eslint = function()
			-- 	Snacks.util.lsp.on({}, function(_, client)
			-- 		if client.name == "eslint" then
			-- 			client.server_capabilities.documentFormattingProvider = true
			-- 		elseif client.name == "vtsls" then
			-- 			client.server_capabilities.documentFormattingProvider = false
			-- 		end
			-- 	end)
			-- end,
		},
	},
}
