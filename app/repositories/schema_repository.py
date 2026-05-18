import json
import logging
from typing import Any, Optional

from app.db.session import get_connection

logger = logging.getLogger(__name__)


def create_schema(
    *,
    vendor: str,
    block_name: str,
    block_type: str,
    version: str,
    description: Optional[str],
    pins: list[dict[str, Any]],
    parameters: list[dict[str, Any]],
    notes: Optional[str],
    review_status: str = "Draft",
    changed_by: str = "local-user",
    change_summary: Optional[str] = None,
) -> int:
    logger.info(
        "Creating schema: vendor=%s block_name=%s block_type=%s version=%s",
        vendor,
        block_name,
        block_type,
        version,
    )

    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO block_schemas (
                vendor,
                block_name,
                block_type,
                version,
                description,
                pins_json,
                parameters_json,
                notes,
                review_status,
                changed_by,
                change_summary
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                vendor,
                block_name,
                block_type,
                version,
                description,
                json.dumps(pins),
                json.dumps(parameters),
                notes,
                review_status,
                changed_by,
                change_summary,
            ),
        )
        conn.commit()
        schema_id = int(cursor.lastrowid)

    logger.info("Created schema id=%s", schema_id)
    return schema_id


def list_schemas() -> list[dict[str, Any]]:
    logger.info("Listing schemas from block_schemas")

    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT
                id,
                vendor,
                block_name,
                block_type,
                version,
                description,
                review_status,
                changed_by,
                change_summary,
                created_at,
                updated_at
            FROM block_schemas
            ORDER BY vendor ASC, block_name ASC, created_at DESC, id DESC
            """
        ).fetchall()

    return [dict(row) for row in rows]


def get_schema(schema_id: int) -> Optional[dict[str, Any]]:
    logger.info("Fetching schema by id=%s from block_schemas", schema_id)

    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT
                id,
                vendor,
                block_name,
                block_type,
                version,
                description,
                pins_json,
                parameters_json,
                notes,
                review_status,
                changed_by,
                change_summary,
                created_at,
                updated_at
            FROM block_schemas
            WHERE id = ?
            """,
            (schema_id,),
        ).fetchone()

    if row is None:
        logger.warning("Schema not found for id=%s", schema_id)
        return None

    schema = dict(row)
    schema["pins"] = json.loads(schema.get("pins_json") or "[]")
    schema["parameters"] = json.loads(schema.get("parameters_json") or "[]")

    return schema


def fetch_all_schemas() -> list[dict[str, Any]]:
    return list_schemas()


def fetch_schema_by_id(schema_id: int) -> Optional[dict[str, Any]]:
    return get_schema(schema_id)
