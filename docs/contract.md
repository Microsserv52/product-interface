---
icon: lucide/route
---

# Contract

## Endpoints

| Method | Path | Authentication | Success | Errors |
| --- | --- | --- | --- | --- |
| `GET` | `/products` | Public | `200` | `503` |
| `POST` | `/products` | `ROLE_ADMIN` | `201` | `400`, `401`, `403`, `409`, `413`, `503` |
| `GET` | `/products/{id}` | Public | `200` | `400`, `404`, `503` |
| `DELETE` | `/products/{id}` | `ROLE_ADMIN` | `204` | `400`, `401`, `403`, `404`, `503` |
| `POST` | `/products/{id}/image/uploads` | `ROLE_ADMIN` | `201` | `400`, `401`, `403`, `404`, `413`, `503` |
| `POST` | `/products/{id}/image` | `ROLE_ADMIN` | `200` | `400`, `401`, `403`, `404`, `409`, `503` |
| `PATCH` | `/products/{id}/image` | `ROLE_ADMIN` | `200` | `400`, `401`, `403`, `404`, `503` |
| `DELETE` | `/products/{id}/image` | `ROLE_ADMIN` | `200` | `400`, `401`, `403`, `404`, `503` |

## Product

```json
{
  "id": "0195abfb-7074-73a9-9d26-b4b9fbaab0a8",
  "name": "Tomato",
  "price": 10.12,
  "unit": "kg"
}
```

| Field | Type | Rules |
| --- | --- | --- |
| `id` | UUID string | Server generated. |
| `name` | string | 1-120 characters. |
| `price` | number | `0.01`-`9999999999.99`, at most two decimals, USD. |
| `unit` | string | 1-32 characters. |
| `image` | object or `null` | Always serialized. See [Image](#image). |

## Image

Every product serializes an `image` field, either `null` or an object:

```json
{
  "id": "0195abfb-7074-73a9-9d26-b4b9fbaab0a8",
  "name": "Tomato",
  "price": 10.12,
  "unit": "kg",
  "image": {
    "url": "/media/media/products/0195abfb-7074-73a9-9d26-b4b9fbaab0a8/0195ac10-5c1f-7c2a-9f3d-9a5b0b0e7a13/original.jpg",
    "alt": "Fresh ripe tomatoes",
    "width": 1200,
    "height": 1000
  }
}
```

| Field | Type | Rules |
| --- | --- | --- |
| `image.url` | string | Public URL. Served read-only from the media origin (media bucket via CloudFront in prod, `/media/` edge path locally). |
| `image.alt` | string | 1-200 characters. |
| `image.width` | integer | 1-4096. |
| `image.height` | integer | 1-4096. |

Images are uploaded in two steps:

1. `POST /products/{id}/image/uploads` with `fileName`, `contentType`
   (`image/jpeg` or `image/png`), declared `size` (bytes), `width` and `height`
   returns `201` with `uploadId`, `uploadUrl`, `uploadHeaders` and an
   `expiresAt` timestamp. `uploadHeaders` always includes `If-None-Match: *`.
2. The caller `PUT`s the raw bytes to `uploadUrl` with those headers, then
   attaches the result with `POST /products/{id}/image` and the `uploadId`
   plus an `alt` string. Attach validates the stored bytes (type, size,
   dimensions, single `media/products/{productId}/{assetId}/original.{ext}`
   key), replaces any existing image and returns the full product.

`PATCH /products/{id}/image` updates only the alt text. `DELETE
/products/{id}/image` removes the stored object and returns the product with
`image: null`. Only `image/jpeg` and `image/png` are accepted, up to 5 MiB and
16 million pixels.

## Create request

```json
{
  "name": "Tomato",
  "price": 10.12,
  "unit": "kg"
}
```

## Error envelope

```json
{
  "code": "VALIDATION_ERROR",
  "message": "Request validation failed",
  "details": [
    { "field": "price", "message": "must be greater than or equal to 0.01" }
  ]
}
```

| Code | Status | Meaning |
| --- | --- | --- |
| `VALIDATION_ERROR` | `400` | Invalid input. |
| `INVALID_REQUEST` | `400` | Malformed JSON or invalid identifier. |
| `UNAUTHORIZED` | `401` | Missing or invalid token. |
| `FORBIDDEN` | `403` | Token lacks `ROLE_ADMIN`. |
| `PRODUCT_NOT_FOUND` | `404` | Unknown product, or image alt updated with no image attached. |
| `IDEMPOTENCY_KEY_REUSED` | `409` | Key reused with a different body. |
| `IMAGE_ALREADY_EXISTS` | `409` | A validated image already exists for this upload. |
| `PAYLOAD_TOO_LARGE` | `413` | Body exceeded the configured limit. |
| `DEPENDENCY_UNAVAILABLE` | `503` | PostgreSQL is unavailable. |

!!! warning "Authentication boundary"

    Gateway applies the public policy: catalogue reads are public and product
    writes require `ROLE_ADMIN`. Product enforces the same policy locally so a
    direct caller cannot bypass it.

## Idempotency

`POST /products` accepts `Idempotency-Key` (1-128 characters, `[A-Za-z0-9._:-]`).
The service stores the key with a hash of the normalized request and the
created product. A replay returns the original `201` response; a different
body returns `409`. Keys are deployment-scoped and retained with the product.

## Machine-readable files

- [OpenAPI](../openapi/product.yaml)
- [Product schema](../schemas/product.schema.json)
- [Input schema](../schemas/product-input.schema.json)
- [List schema](../schemas/product-list.schema.json)
- [Error schema](../schemas/error.schema.json)
