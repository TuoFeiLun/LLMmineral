"""
SQLite schema creation and helpers for MineralAssistant.
"""

import os
import sqlite3
from pathlib import Path
from typing import Optional


PROJECT_ROOT = Path(__file__).parent.parent
DB_PATH = str(PROJECT_ROOT / "MineralAssistant.db")


def get_connection() -> sqlite3.Connection:
    """Open a SQLite connection with foreign keys enabled."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def initialize_database() -> None:
    """Create tables if not exist and seed base data."""
    os.makedirs(PROJECT_ROOT, exist_ok=True)
    with get_connection() as conn:
        cur = conn.cursor()

        # LLM models
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS llmmodel (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            );
            """
        )

        # Conversation: container for many query questions
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS conversation (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT DEFAULT (datetime('now'))
            );
            """
        )

        # Each user question/answer pair within a conversation
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS queryquestion (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question TEXT NOT NULL,
                llmmodel_id INTEGER NOT NULL,
                conversation_id INTEGER NOT NULL,
                answer TEXT,
                sourcetrace TEXT,
                thinktime REAL,
                send_time TEXT,
                finish_time TEXT,
                FOREIGN KEY (llmmodel_id) REFERENCES llmmodel(id) ON DELETE RESTRICT,
                FOREIGN KEY (conversation_id) REFERENCES conversation(id) ON DELETE CASCADE
            );
            """
        )

        # Uploaded corpus files
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS corpus (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_name TEXT NOT NULL,
                file_path TEXT NOT NULL,
                converted_status INTEGER NOT NULL DEFAULT 0,
                vectordatabase_id INTEGER,
                uploaded_at TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (vectordatabase_id) REFERENCES vectordatabase(id) ON DELETE SET NULL
            );
            """
        )

        # Vector DB collections produced from corpus
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS vectordatabase (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                collection_name TEXT NOT NULL UNIQUE,
                db_path TEXT NOT NULL DEFAULT "/datastore/simple_geological_db",
                using_status INTEGER NOT NULL DEFAULT 1
                
            );
            """
        )

        # Seed LLM models if empty
        cur.execute("SELECT COUNT(1) FROM llmmodel;")
        (count,) = cur.fetchone()
        if count == 0:
            cur.executemany(
                "INSERT INTO llmmodel(name) VALUES (?);",
                [
                    ("qwen2.5-7b",),
                    ("llama3.1-7b",),
                ],
            )

        # Seed initial vectordatabase collections if empty
        cur.execute("SELECT COUNT(1) FROM vectordatabase;")
        (count,) = cur.fetchone()
        if count == 0:
            cur.executemany(
                "INSERT INTO vectordatabase(collection_name, db_path, using_status) VALUES (?, ?, ?);",
                [
                    ("extra_documents2", "/datastore/simple_geological_db", 1),
                    ("QLD_Stratigraphic", "/datastore/simple_geological_db", 1),
                    ("documents", "/datastore/simple_geological_db", 1),
                ],
            )

        conn.commit()


def get_llm_model_id_by_name(name: str) -> Optional[int]:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT id FROM llmmodel WHERE name = ?;", (name,))
        row = cur.fetchone()
        return row[0] if row else None


initialize_database()