"""
Corpus table helpers.
"""

from typing import Any, Dict, Optional
from .creatSQL import get_connection


def insert_corpus(
    file_name: str,
    file_path: str,
    converted_status: int = 0,
    vectordatabase_id: Optional[int] = None,
) -> int:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO corpus (file_name, file_path, converted_status, vectordatabase_id)
            VALUES (?, ?, ?, ?);
            """,
            (file_name, file_path, converted_status, vectordatabase_id),
        )
        return cur.lastrowid


def mark_converted(corpus_id: int, vectordatabase_id: int) -> None:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            "UPDATE corpus SET converted_status = 1, vectordatabase_id = ? WHERE id = ?;",
            (vectordatabase_id, corpus_id),
        )


def get_corpus(corpus_id: int) -> Optional[Dict[str, Any]]:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT id, file_name, file_path, converted_status, vectordatabase_id, uploaded_at FROM corpus WHERE id = ?;",
            (corpus_id,),
        )
        row = cur.fetchone()
        if not row:
            return None
        return {
            "id": row[0],
            "file_name": row[1],
            "file_path": row[2],
            "converted_status": row[3],
            "vectordatabase_id": row[4],
            "uploaded_at": row[5],
        }
