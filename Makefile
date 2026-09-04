.PHONY: install
install: ## Install the virtual environment and install the pre-commit hooks
	@if [ ! -d .git ]; then \
		echo "❌ Error: Not a git repository. Run 'git init -b main' first (see README step 1)."; \
		exit 1; \
	fi
	@echo "🚀 Creating virtual environment using uv"
	@uv sync
	@uv run pre-commit install

# Where the shared governance artefacts live. The parity and naming renderers read naming.toml
# and parity.toml out of this checkout at the tag pinned in pyproject.toml, never from its
# working tree. Same variable, same meaning, same default as in idfkit.
CONFORMANCE_REPO ?= ../idfkit-conformance

.PHONY: check-page-kinds
check-page-kinds: ## Verify every page declares the kind it is written as
	@echo "🚀 Checking that every page declares its kind"
	@uv run python scripts/check_page_kinds.py

.PHONY: check-capabilities
check-capabilities: ## Verify every capability page declares the capability it describes
	@echo "🚀 Checking that every capability page declares a capability"
	@uv run python scripts/check_capability_declarations.py

.PHONY: check-engine-assets
check-engine-assets: ## Verify the built site hosts no engine bytes
	@if [ -d site ]; then \
		echo "🚀 Checking the built site hosts no engine bytes"; \
		uv run python scripts/check_engine_assets.py site; \
	else \
		echo "⏭️  Skipping engine-asset check (no build in site/; run 'make docs-test' first)"; \
	fi

.PHONY: check-vendored
check-vendored: ## Verify the vendored TypeScript trees match the pinned docs level
	@echo "🚀 Checking the vendored TypeScript artifacts against the pinned docs level"
	@uv run python scripts/sync_js_artifacts.py --check

.PHONY: check-governance-reader
check-governance-reader: ## Verify the duplicated governance reader has not drifted from the library's
	@echo "🚀 Checking the duplicated governance reader against idfkit"
	@uv run python -m pytest tests/test_governance_source_matches.py -q

.PHONY: check
check: check-page-kinds check-capabilities check-engine-assets check-vendored check-governance-reader ## Run code quality tools.
	@echo "🚀 Checking lock file consistency with 'pyproject.toml'"
	@uv lock --locked
	@echo "🚀 Linting code: Running pre-commit"
	@uv run pre-commit run -a
	@echo "🚀 Static type checking: Running pyright"
	@uv run pyright scripts/ docs/hooks docs/snippets

.PHONY: test
test: ## Test the code with pytest
	@echo "🚀 Testing code: Running pytest"
	@uv run python -m pytest --cov --cov-config=pyproject.toml --cov-report=xml

.PHONY: docs-test
docs-test: ## Test if documentation can be built without warnings or errors
	@./scripts/build_docs.sh -s
	@echo "🚀 Checking the built site hosts no engine bytes"
	@uv run python scripts/check_engine_assets.py site

.PHONY: docs
docs: ## Build and serve the documentation
	@uv run mkdocs serve

.PHONY: help
help:
	@uv run python -c "import re; \
	[[print(f'\033[36m{m[0]:<20}\033[0m {m[1]}') for m in re.findall(r'^([a-zA-Z_-]+):.*?## (.*)$$', open(makefile).read(), re.M)] for makefile in ('$(MAKEFILE_LIST)').strip().split()]"

.DEFAULT_GOAL := help
