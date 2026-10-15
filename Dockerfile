FROM ghcr.io/astral-sh/uv:0.9.25 AS uv-binary

FROM python:3.12-slim AS builder

COPY --from=uv-binary /uv /uvx /bin/

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1 \
	UV_LINK_MODE=copy

COPY requirements.txt ./requirements.txt
RUN uv venv /opt/venv && \
    uv pip install --python /opt/venv --compile --no-cache-dir -r requirements.txt


FROM python:3.12-slim AS runtime

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
	PYTHONUNBUFFERED=1 \
	PATH="/opt/venv/bin:$PATH"

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
RUN useradd --create-home --shell /bin/bash appuser
RUN mkdir -p /app/data && chown -R appuser:appuser /app/data

COPY --from=builder /opt/venv /opt/venv
COPY --chown=appuser:appuser . .

USER appuser
EXPOSE 8888


ENTRYPOINT ["/entrypoint.sh"]
CMD ["python", "src/main.py"]