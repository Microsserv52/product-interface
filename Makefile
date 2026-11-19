.PHONY: bootstrap validate lint format-check build clean

bootstrap:
	./scripts/bootstrap.sh

validate:
	docker build --tag product-interface-validator:local .
	docker run --rm product-interface-validator:local

lint:
	uv run ruff format --check scripts
	uv run ruff check scripts

format-check: lint

build:
	docker build --tag product-interface-validator:local .

clean:
	rm -rf .venv site
