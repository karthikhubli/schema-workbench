import logging
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
DB_PATH = BASE_DIR / "schema_workbench.db"

logger = logging.getLogger(__name__)


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS block_schemas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                vendor TEXT NOT NULL,
                block_name TEXT NOT NULL,
                block_type TEXT NOT NULL,
                version TEXT NOT NULL,
                description TEXT,
                pins_json TEXT NOT NULL DEFAULT '[]',
                parameters_json TEXT NOT NULL DEFAULT '[]',
                notes TEXT,
                review_status TEXT NOT NULL DEFAULT 'Draft',
                changed_by TEXT NOT NULL DEFAULT 'local-user',
                change_summary TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS mappings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_schema_id INTEGER NOT NULL,
                target_schema_id INTEGER NOT NULL,
                mapping_json TEXT NOT NULL DEFAULT '[]',
                notes TEXT,
                review_status TEXT NOT NULL DEFAULT 'Draft',
                changed_by TEXT NOT NULL DEFAULT 'local-user',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(source_schema_id) REFERENCES block_schemas(id),
                FOREIGN KEY(target_schema_id) REFERENCES block_schemas(id)
            )
            """
        )

        conn.commit()


def reset_db():
    logger.info("Cleaning DB at %s", DB_PATH)
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DROP TABLE IF EXISTS mappings")
    cursor.execute("DROP TABLE IF EXISTS block_schemas")
    cursor.execute("DROP TABLE IF EXISTS vendors")

    conn.commit()
    conn.close()
