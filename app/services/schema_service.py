import json
import logging
from collections import defaultdict
from typing import Any

from app.models.schema_models import BlockSchema
from app.repositories import schema_repository

logger = logging.getLogger(__name__)


def _load_json_array(value: str, field_name: str) -> list[dict[str, Any]]:
    try:
        parsed = json.loads(value or "[]")
    except json.JSONDecodeError as exc:
        raise ValueError(f"{field_name} must be valid JSON") from exc

    if not isinstance(parsed, list):
        raise ValueError(f"{field_name} must be a JSON array")

    return parsed


def save_schema_from_form(
    *,
    vendor: str,
    block_name: str,
    block_type: str,
    version: str,
    description: str,
    pins_json: str,
    parameters_json: str,
    notes: str,
    review_status: str = "Draft",
    changed_by: str = "local-user",
    change_summary: str = "",
) -> int:
    pins = _load_json_array(pins_json, "Pins JSON")
    parameters = _load_json_array(parameters_json, "Parameters JSON")

    schema = BlockSchema(
        vendor=vendor,
        block_name=block_name,
        block_type=block_type,
        version=version,
        description=description,
        pins=pins,
        parameters=parameters,
        notes=notes,
    )

    data = schema.model_dump() if hasattr(schema, "model_dump") else schema.dict()

    schema_id = schema_repository.create_schema(
        vendor=data["vendor"],
        block_name=data["block_name"],
        block_type=data["block_type"],
        version=data["version"],
        description=data.get("description"),
        pins=data["pins"],
        parameters=data["parameters"],
        notes=data.get("notes"),
        review_status=review_status,
        changed_by=changed_by,
        change_summary=change_summary,
    )

    logger.info(
        "Saved schema id=%s vendor=%s block_name=%s version=%s",
        schema_id,
        vendor,
        block_name,
        version,
    )
    return schema_id


def list_schemas() -> list[dict[str, Any]]:
    return schema_repository.list_schemas()


def get_all_schemas() -> list[dict[str, Any]]:
    return schema_repository.list_schemas()


def group_schemas_by_vendor() -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for schema in get_all_schemas():
        grouped[schema["vendor"]].append(schema)
    return dict(grouped)


def get_schema_by_id(schema_id: int):
    return schema_repository.get_schema(schema_id)
