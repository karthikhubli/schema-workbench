import json
import logging
from typing import Any, Optional

from app.db.session import get_connection

logger = logging.getLogger(__name__)


def create_mapping(
    *,
    source_schema_id: int,
    target_schema_id: int,
    mapping_items: list[dict[str, Any]],
    notes: Optional[str],
    review_status: str = "Draft",
    changed_by: str = "local-user",
) -> int:
    logger.info(
        "Creating mapping source_schema_id=%s target_schema_id=%s items=%s",
        source_schema_id,
        target_schema_id,
        len(mapping_items),
    )

    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO mappings (
                source_schema_id,
                target_schema_id,
                mapping_json,
                notes,
                review_status,
                changed_by
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                source_schema_id,
                target_schema_id,
                json.dumps(mapping_items),
                notes,
                review_status,
                changed_by,
            ),
        )
        conn.commit()
        mapping_id = int(cursor.lastrowid)

    logger.info("Created mapping id=%s", mapping_id)
    return mapping_id


def list_mappings() -> list[dict[str, Any]]:
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT
                m.id,
                m.source_schema_id,
                m.target_schema_id,
                m.mapping_json,
                m.notes,
                m.review_status,
                m.changed_by,
                m.created_at,
                source.vendor || ' / ' || source.block_name || ' (' || source.block_type || ') v' || source.version AS source_label,
                target.vendor || ' / ' || target.block_name || ' (' || target.block_type || ') v' || target.version AS target_label
            FROM mappings m
            JOIN block_schemas source ON source.id = m.source_schema_id
            JOIN block_schemas target ON target.id = m.target_schema_id
            ORDER BY m.created_at DESC, m.id DESC
            """
        ).fetchall()

    return [dict(row) for row in rows]
