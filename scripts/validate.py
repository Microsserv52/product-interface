#!/usr/bin/env python3
"""Validate the canonical Product contract and its published examples."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator
from openapi_spec_validator import validate
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT202012

ROOT = Path(__file__).resolve().parent.parent
OPENAPI = ROOT / "openapi" / "product.yaml"
SCHEMA_DIR = ROOT / "schemas"

EXAMPLES = {
    "examples/product.json": "product.schema.json",
    "examples/product-with-image.json": "product.schema.json",
    "examples/products.json": "product-list.schema.json",
    "examples/product-create.json": "product-input.schema.json",
    "examples/error-validation.json": "error.schema.json",
    "examples/error-not-found.json": "error.schema.json",
    "examples/error-dependency-unavailable.json": "error.schema.json",
}


def load(path: Path) -> Any:
    with path.open(encoding="utf-8") as handle:
        if path.suffix in {".yaml", ".yml"}:
            return yaml.safe_load(handle)
        return json.load(handle)


def build_registry(schemas: dict[str, Any]) -> Registry:
    resources = [
        (
            schema["$id"],
            Resource.from_contents(schema, default_specification=DRAFT202012),
        )
        for schema in schemas.values()
        if schema.get("$id")
    ]
    return Registry().with_resources(resources)


def main() -> int:
    failures: list[str] = []
    document = load(OPENAPI)
    try:
        validate(document)
    except Exception as error:  # noqa: BLE001 - report the validator message verbatim
        failures.append(f"OpenAPI validation failed: {error}")

    schemas = {
        path.name: load(path) for path in sorted(SCHEMA_DIR.glob("*.schema.json"))
    }
    for name, schema in schemas.items():
        try:
            Draft202012Validator.check_schema(schema)
        except Exception as error:  # noqa: BLE001
            failures.append(f"Invalid JSON Schema {name}: {error}")

    registry = build_registry(schemas)
    validators = {
        name: Draft202012Validator(schema, registry=registry)
        for name, schema in schemas.items()
    }

    for relative, schema_name in EXAMPLES.items():
        payload = load(ROOT / relative)
        if schema_name not in validators:
            failures.append(f"{relative} references unknown schema {schema_name}")
            continue
        errors = sorted(
            validators[schema_name].iter_errors(payload), key=lambda item: item.path
        )
        for error in errors:
            failures.append(f"{relative}: {error.message}")

    if failures:
        print("Contract validation failed:", file=sys.stderr)
        for failure in failures:
            print(f" - {failure}", file=sys.stderr)
        return 1

    print(
        f"Validated OpenAPI, {len(schemas)} schemas and {len(EXAMPLES)} examples.",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
