# Product interface

Canonical HTTP contract for the [Microsserv52 Product service](https://github.com/Microsserv52/product).
The contract is published independently so Order, frontend clients and contract
tests can consume the exact version without cloning the service or the
[platform repository](https://github.com/Microsserv52/platform).

[![Contract validation](https://github.com/Microsserv52/product-interface/actions/workflows/ci.yml/badge.svg)](https://github.com/Microsserv52/product-interface/actions/workflows/ci.yml)
[![Documentation](https://github.com/Microsserv52/product-interface/actions/workflows/docs.yml/badge.svg)](https://microsserv52.github.io/product-interface/)

> [!IMPORTANT]
> This repository contains contract artifacts only. It has no database, no
> persistence and no framework internals. The runnable service lives in
> [`Microsserv52/product`](https://github.com/Microsserv52/product).

## Quick start

```bash
git clone https://github.com/Microsserv52/product-interface.git
cd product-interface
./scripts/bootstrap.sh
```

`bootstrap.sh` validates the OpenAPI document, every JSON Schema and every
example. It prefers Docker and falls back to local `uv` only when Docker is not
available. No runtime container is required for consumers: the published
artifacts are plain YAML and JSON files.

## Artifacts

| Artifact | Purpose |
| --- | --- |
| [`openapi/product.yaml`](openapi/product.yaml) | Canonical OpenAPI 3.1 document. |
| [`schemas/product.schema.json`](schemas/product.schema.json) | Product response schema. |
| [`schemas/product-input.schema.json`](schemas/product-input.schema.json) | Product creation request schema. |
| [`schemas/product-list.schema.json`](schemas/product-list.schema.json) | Product list schema. |
| [`schemas/error.schema.json`](schemas/error.schema.json) | Stable error envelope with optional field details. |
| [`examples/`](examples/) | Valid response, request and error examples. |

## Endpoints

| Method | Path | Authentication | Success |
| --- | --- | --- | --- |
| `GET` | `/products` | Public | `200` product array |
| `POST` | `/products` | `ROLE_ADMIN` | `201` product |
| `GET` | `/products/{id}` | Public | `200` product |
| `DELETE` | `/products/{id}` | `ROLE_ADMIN` | `204` |
| `POST` | `/products/{id}/image/uploads` | `ROLE_ADMIN` | `201` upload ticket |
| `POST` | `/products/{id}/image` | `ROLE_ADMIN` | `200` product |
| `PATCH` | `/products/{id}/image` | `ROLE_ADMIN` | `200` product |
| `DELETE` | `/products/{id}/image` | `ROLE_ADMIN` | `200` product with `image: null` |

`POST /products` also accepts an optional `Idempotency-Key` header. Replaying
the same key with the same body returns the original product. Reusing the key
with a different body returns `409 IDEMPOTENCY_KEY_REUSED`.

Product images use a two-step upload. `POST /products/{id}/image/uploads`
returns a short-lived presigned `uploadUrl` plus the `uploadHeaders` (always
including `If-None-Match: *`) to send the bytes with; the caller then attaches
the result with `POST /products/{id}/image` and the ticket's `uploadId`. Only
`image/jpeg` and `image/png` are accepted, up to 5 MiB and 16 million pixels.
Attach validates the stored bytes, replaces any existing image and returns the
full product. `PATCH` updates only the alt text; `DELETE` removes the stored
object and returns the product with `image: null`.

## Consuming the contract

1. Pin a release tag or commit SHA from this repository.
2. Read `openapi/product.yaml` into your client generator, gateway
   configuration or contract test.
3. Keep the generated client version aligned with the service release notes.
4. Treat unknown error fields and additional response fields as forward
   compatible; required fields and status codes are stable.

```bash
# Example: validate a captured response with the published schema
uvx --from jsonschema check-jsonschema \
  --schemafile schemas/product.schema.json response.json
```

## Versioning

The contract follows semantic versioning:

- **MAJOR** — removed or renamed required fields, changed status codes or
  authentication rules.
- **MINOR** — additive optional fields or new endpoints.
- **PATCH** — documentation, examples or non-behavioral clarifications.

Every service release records the interface version it implements. See
[Versioning](docs/versioning.md).

## Validation commands

```bash
make bootstrap   # container-first contract validation
make validate    # force Docker validation
make lint        # Ruff formatting and lint checks
```

## Links

- [Microsserv52 organization](https://github.com/Microsserv52)
- [Platform repository](https://github.com/Microsserv52/platform)
- [Published platform documentation](https://microsserv52.github.io/platform/)
- [Product service repository](https://github.com/Microsserv52/product)
- [Product interface documentation](https://microsserv52.github.io/product-interface/)
