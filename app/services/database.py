"""SQLite persistence layer for transformed jobs."""
import json
import sqlite3
from pathlib import Path

DB_PATH = Path("etl.db")

_CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS transform_jobs (
    id          TEXT PRIMARY KEY,
    name        TEXT NOT NULL,
    transformer TEXT NOT NULL,
    created_at  TEXT NOT NULL,
    records_json TEXT NOT NULL
);
"""


def init_db() -> None:
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(_CREATE_TABLE)
        conn.commit()


def insert_job(job_id: str, name: str, transformer: str, created_at: str, records: list[dict]) -> None:
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT INTO transform_jobs (id, name, transformer, created_at, records_json) VALUES (?, ?, ?, ?, ?)",
            (job_id, name, transformer, created_at, json.dumps(records)),
        )
        conn.commit()


def list_jobs() -> list[dict]:
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT id, name, created_at FROM transform_jobs ORDER BY created_at DESC"
        ).fetchall()
    return [dict(r) for r in rows]


def get_job(job_id: str) -> dict | None:
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute(
            "SELECT id, name, created_at, records_json FROM transform_jobs WHERE id = ?",
            (job_id,),
        ).fetchone()
    if row is None:
        return None
    data = dict(row)
    data["records"] = json.loads(data.pop("records_json"))
    return data


def delete_job(job_id: str) -> bool:
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute("DELETE FROM transform_jobs WHERE id = ?", (job_id,))
        conn.commit()
    return cursor.rowcount > 0
