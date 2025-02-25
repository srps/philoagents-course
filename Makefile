# --- Default Values ---

CHECK_DIRS := .

# --- Infrastructure ---

infrastructure-up:
	docker compose up --build -d

infrastructure-stop:
	docker compose stop


# OFFLINE PIPELINES

rag-ingestion:
	uv run python -m tools.create_long_term_memory

delete-long-term-memory:
	uv run python -m tools.delete_long_term_memory

evaluate-agent:
	uv run python -m tools.evaluate_agent

# --- QA ---

format-fix:
	uv run ruff format $(CHECK_DIRS)
	uv run ruff check --select I --fix 

lint-fix:
	uv run ruff check --fix

format-check:
	uv run ruff format --check $(CHECK_DIRS) 
	uv run ruff check -e
	uv run ruff check --select I -e

lint-check:
	uv run ruff check $(CHECK_DIRS)
