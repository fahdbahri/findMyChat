FROM python:3.12-slim-bookworm AS base


COPY --from=ghcr.io/astral-sh/uv:0.8.10 /uv /uvx /bin/


WORKDIR /app


COPY uv.lock pyproject.toml ./


COPY . .


RUN uv sync --locked 


FROM base AS app


WORKDIR /app














