import json
import logging
from collections import defaultdict
from typing import Any

from app.models.schema_models import BlockSchema
from app.repositories import schema_repository, mapping_repository

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


def _index_by_name(items: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {
        str(item.get("name", "")).strip().lower(): item
        for item in items
        if str(item.get("name", "")).strip()
    }


def analyze_breaking_change(
    *,
    previous_schema: dict[str, Any],
    new_pins: list[dict[str, Any]],
    new_parameters: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    Prototype-level breaking-change detector.

    Breaking changes:
    - Existing pin/parameter removed
    - Existing pin direction or type changed
    - Existing parameter type changed
    - New mandatory pin/parameter added
    """

    reasons: list[str] = []

    old_pins = _index_by_name(previous_schema.get("pins", []))
    old_params = _index_by_name(previous_schema.get("parameters", []))
    next_pins = _index_by_name(new_pins)
    next_params = _index_by_name(new_parameters)

    for name, old_pin in old_pins.items():
        if name not in next_pins:
            reasons.append(f"Pin removed: {old_pin.get('name')}")
            continue

        new_pin = next_pins[name]
        if str(old_pin.get("dir", "")).lower() != str(new_pin.get("dir", "")).lower():
            reasons.append(f"Pin direction changed: {old_pin.get('name')}")

        if str(old_pin.get("type", "")).lower() != str(new_pin.get("type", "")).lower():
            reasons.append(f"Pin type changed: {old_pin.get('name')}")

    for name, new_pin in next_pins.items():
        if name not in old_pins and bool(new_pin.get("mandatory")):
            reasons.append(f"New mandatory pin added: {new_pin.get('name')}")

    for name, old_param in old_params.items():
        if name not in next_params:
            reasons.append(f"Parameter removed: {old_param.get('name')}")
            continue

        new_param = next_params[name]
        if str(old_param.get("type", "")).lower() != str(new_param.get("type", "")).lower():
            reasons.append(f"Parameter type changed: {old_param.get('name')}")

    for name, new_param in next_params.items():
        if name not in old_params and bool(new_param.get("mandatory")):
            reasons.append(f"New mandatory parameter added: {new_param.get('name')}")

    return {
        "is_breaking": len(reasons) > 0,
        "reasons": reasons,
    }


def save_schema_new_version_from_form(
    *,
    original_schema_id: int,
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
    change_summary: str = "New version created from existing schema",
) -> dict[str, Any]:
    previous_schema = get_schema_by_id(original_schema_id)

    pins = _load_json_array(pins_json, "Pins JSON")
    parameters = _load_json_array(parameters_json, "Parameters JSON")

    breaking_result = {
        "is_breaking": False,
        "reasons": [],
    }

    if previous_schema:
        breaking_result = analyze_breaking_change(
            previous_schema=previous_schema,
            new_pins=pins,
            new_parameters=parameters,
        )

    schema_id = save_schema_from_form(
        vendor=vendor,
        block_name=block_name,
        block_type=block_type,
        version=version,
        description=description,
        pins_json=pins_json,
        parameters_json=parameters_json,
        notes=notes,
        review_status=review_status,
        changed_by=changed_by,
        change_summary=change_summary,
    )

    mappings_marked = 0
    if breaking_result["is_breaking"]:
        mappings_marked = mapping_repository.mark_mappings_needing_update_for_block(
            vendor=vendor,
            block_name=block_name,
            changed_by=changed_by,
        )

    return {
        "schema_id": schema_id,
        "is_breaking": breaking_result["is_breaking"],
        "reasons": breaking_result["reasons"],
        "mappings_marked": mappings_marked,
    }
