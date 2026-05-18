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


def mark_mappings_needing_update_for_block(
    *,
    vendor: str,
    block_name: str,
    changed_by: str = "local-user",
) -> int:
    logger.info(
        "Marking mappings as Needs Update for vendor=%s block_name=%s",
        vendor,
        block_name,
    )

    with get_connection() as conn:
        cursor = conn.execute(
            """
            UPDATE mappings
            SET
                review_status = 'Needs Update',
                changed_by = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE source_schema_id IN (
                SELECT id
                FROM block_schemas
                WHERE vendor = ? AND block_name = ?
            )
            OR target_schema_id IN (
                SELECT id
                FROM block_schemas
                WHERE vendor = ? AND block_name = ?
            )
            """,
            (
                changed_by,
                vendor,
                block_name,
                vendor,
                block_name,
            ),
        )
        conn.commit()
        updated_count = cursor.rowcount

    logger.info("Marked %s mappings as Needs Update", updated_count)
    return int(updated_count)
