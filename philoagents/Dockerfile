FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim

WORKDIR /app

COPY uv.lock pyproject.toml README.md ./

RUN uv sync --frozen --no-cache

COPY philoagents philoagents/
COPY tools tools/
COPY data data/

CMD ["/app/.venv/bin/fastapi", "run", "philoagents/infrastructure/api.py", "--port", "8000", "--host", "0.0.0.0"]
