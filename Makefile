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
