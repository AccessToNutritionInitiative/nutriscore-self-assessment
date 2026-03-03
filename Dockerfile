FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

ENV PORT=8000

WORKDIR /app

# Copy dependency files first for layer caching
COPY pyproject.toml uv.lock ./

# Install production dependencies (without the project itself)
RUN uv sync --frozen --no-dev --no-install-project

# Copy source code and install the project
COPY . .
RUN uv sync --frozen --no-dev

EXPOSE ${PORT}

CMD ["sh", "-c", "uv run uvicorn nutri.interface.api.main:app --host 0.0.0.0 --port ${PORT}"]
