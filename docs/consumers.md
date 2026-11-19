---
icon: lucide/users
---

# Consumers

## Generate a client

```bash
git clone --branch v0.1.0 https://github.com/Microsserv52/product-interface.git
npx @openapitools/openapi-generator-cli generate \
  -i product-interface/openapi/product.yaml \
  -g typescript-fetch \
  -o generated/product-client
```

## Validate captured payloads

```bash
uvx --from jsonschema check-jsonschema \
  --schemafile schemas/product.schema.json product.json
```

## Contract tests in a service

1. Copy the pinned `schemas/` and `openapi/` artifacts into your test
   resources, or check out this repository in CI.
2. Validate every success payload against the matching schema.
3. Validate every error payload against `error.schema.json`.
4. Assert status codes and authentication rules from the OpenAPI document.

The Product service follows this approach and fails CI if its contract snapshot
differs from this repository.
