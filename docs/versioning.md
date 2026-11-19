---
icon: lucide/git-branch
---

# Versioning

The contract uses semantic versioning and is identified by the repository tag.

| Change | Version |
| --- | --- |
| Remove or rename a required field, change a status code or auth rule | MAJOR |
| Add an optional field, endpoint or error code | MINOR |
| Documentation, examples, schema metadata | PATCH |

## Compatibility rules

- Clients must ignore unknown optional fields.
- Servers must not remove required fields within a major version.
- New enum values are additive; clients should tolerate unknown error codes.
- `price` remains a JSON number and `id` remains a UUID string.
- Public reads remain public; admin writes remain protected within a major
  version.

## Service alignment

The Product service records the interface tag it implements in its changelog
and README. A service release must not publish before its contract checks pass
against this repository.
