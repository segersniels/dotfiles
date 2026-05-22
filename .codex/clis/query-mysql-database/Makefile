PREFIX ?= $(HOME)/.local
BINDIR ?= $(PREFIX)/bin
CARGO ?= cargo

.PHONY: fmt test build install-local

fmt:
	$(CARGO) fmt

test:
	$(CARGO) test

build:
	$(CARGO) build --release

install-local: build
	mkdir -p "$(BINDIR)"
	cp target/release/query-mysql-database "$(BINDIR)/query-mysql-database"
	chmod +x "$(BINDIR)/query-mysql-database"
