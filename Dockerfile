# Multi-stage build con uv oficial de Astral (Regla GDH Modern Speed)
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

WORKDIR /app

# Instalar dependencias con uv cache
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev

# Copiar código fuente
COPY . /app

# Sincronizar el proyecto
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# Etapa final de producción ultra liviana
FROM python:3.12-slim-bookworm

WORKDIR /app

# Copiar el entorno virtual y el código desde el builder
COPY --from=builder /app /app

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
