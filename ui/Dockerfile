FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

ENV UV_SYSTEM_PYTHON=1
ENV PORT=8501

WORKDIR /app

# Install UI dependencies
RUN uv pip install streamlit pandas requests pydantic

COPY . .

CMD ["sh", "-c", "streamlit run app.py --server.port=${PORT} --server.address=0.0.0.0"]
