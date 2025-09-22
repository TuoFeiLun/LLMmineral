"""
Conversation table helpers.
"""

from typing import Any, Dict, List, Optional
from .creatSQL import get_connection


def create_conversation() -> int:
    """Create a new conversation and return its id."""
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("INSERT INTO conversation DEFAULT VALUES;")
        return cur.lastrowid


def get_conversation(conversation_id: int) -> Optional[Dict[str, Any]]:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT id, created_at FROM conversation WHERE id = ?;",
            (conversation_id,),
        )
        row = cur.fetchone()
        if not row:
            return None
        return {"id": row[0], "created_at": row[1]}


def list_conversations(limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT id, created_at FROM conversation ORDER BY id DESC LIMIT ? OFFSET ?;",
            (limit, offset),
        )
        return [{"id": r[0], "created_at": r[1]} for r in cur.fetchall()]


def delete_conversation(conversation_id: int) -> bool:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM conversation WHERE id = ?;", (conversation_id,))
        return cur.rowcount > 0
