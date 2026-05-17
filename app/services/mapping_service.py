import json
import logging
from typing import Any

from app.repositories import mapping_repository

logger = logging.getLogger(__name__)


def _load_mapping_items(mapping_json: str) -> list[dict[str, Any]]:
    try:
        parsed = json.loads(mapping_json or "[]")
    except json.JSONDecodeError as exc:
        raise ValueError("Mapping JSON must be valid JSON") from exc

    if not isinstance(parsed, list):
        raise ValueError("Mapping JSON must be a JSON array")

    return parsed


def save_mapping_from_form(
    *,
    source_schema_id: int,
    target_schema_id: int,
    mapping_json: str,
    notes: str,
    status: str = "Draft",
) -> int:
    mapping_items = _load_mapping_items(mapping_json)

    mapping_id = mapping_repository.create_mapping(
        source_schema_id=source_schema_id,
        target_schema_id=target_schema_id,
        mapping_items=mapping_items,
        notes=notes,
        review_status=status,
    )

    logger.info("Saved mapping id=%s", mapping_id)
    return mapping_id


def list_mappings() -> list[dict[str, Any]]:
    return mapping_repository.list_mappings()
