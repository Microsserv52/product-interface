FROM python:3.14.10-slim-trixie

COPY --from=ghcr.io/astral-sh/uv:0.13.8 /uv /bin/uv

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /contract
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project
COPY . /contract

ENTRYPOINT ["uv", "run", "--no-sync", "python", "scripts/validate.py"]
