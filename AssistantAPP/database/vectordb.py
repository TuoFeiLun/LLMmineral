"""
Vector database table helpers.
"""

from typing import Any, Dict, Optional
from .creatSQL import get_connection


def insert_vectordb(
    collection_name: str,
    db_path: str,
    using_status: int = 1,

) -> int:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO vectordatabase (collection_name, db_path, using_status)
            VALUES (?, ?, ?);
            """,
            (collection_name, db_path, using_status),
        )
        return cur.lastrowid


def get_by_collection_name(collection_name: str) -> Optional[Dict[str, Any]]:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT id, collection_name, db_path, using_status FROM vectordatabase WHERE collection_name = ?;",
            (collection_name,),
        )
        row = cur.fetchone()
        if not row:
            return None
        return {
            "id": row[0],
            "collection_name": row[1],
            "db_path": row[2],
            "using_status": row[3],
        }


def set_using_status(vdb_id: int, using_status: int) -> None:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            "UPDATE vectordatabase SET using_status = ? WHERE id = ?;",
            (using_status, vdb_id),
        )
