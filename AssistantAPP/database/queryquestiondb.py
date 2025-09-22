"""
QueryQuestion table helpers.
"""

from typing import Any, Dict, Optional
from .creatSQL import get_connection


def insert_queryquestion(
    question: str,
    llmmodel_id: int,
    conversation_id: int,
    answer: Optional[str],
    sourcetrace: Optional[str],
    thinktime: Optional[float],
    send_time: Optional[str],
    finish_time: Optional[str],
) -> int:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO queryquestion (
                question, llmmodel_id, conversation_id, answer, sourcetrace, thinktime, send_time, finish_time
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?);
            """,
            (
                question,
                llmmodel_id,
                conversation_id,
                answer,
                sourcetrace,
                thinktime,
                send_time,
                finish_time,
            ),
        )
        return cur.lastrowid


def get_queryquestion(record_id: int) -> Optional[Dict[str, Any]]:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT id, question, llmmodel_id, conversation_id, answer, sourcetrace, thinktime, send_time, finish_time
            FROM queryquestion WHERE id = ?;
            """,
            (record_id,),
        )
        row = cur.fetchone()
        if not row:
            return None
        return {
            "id": row[0],
            "question": row[1],
            "llmmodel_id": row[2],
            "conversation_id": row[3],
            "answer": row[4],
            "sourcetrace": row[5],
            "thinktime": row[6],
            "send_time": row[7],
            "finish_time": row[8],
        }
