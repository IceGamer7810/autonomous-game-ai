"""SQLite WAL-backed memory with bounded, queryable records."""

import sqlite3
from pathlib import Path
from typing import Any


class MemoryStore:
    def __init__(self, path: Path | str) -> None:
        self._connection = sqlite3.connect(path)
        self._connection.row_factory = sqlite3.Row
        self._connection.execute("PRAGMA journal_mode=WAL")
        self._connection.execute("PRAGMA foreign_keys=ON")
        self._create_schema()

    def close(self) -> None:
        self._connection.close()

    def _create_schema(self) -> None:
        self._connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                goal TEXT NOT NULL,
                window_id TEXT NOT NULL,
                started_at TEXT NOT NULL,
                ended_at TEXT
            );
            CREATE TABLE IF NOT EXISTS observations (
                id INTEGER PRIMARY KEY,
                session_id TEXT NOT NULL REFERENCES sessions(id),
                frame_hash TEXT NOT NULL,
                summary TEXT NOT NULL,
                confidence REAL NOT NULL CHECK(confidence BETWEEN 0 AND 1),
                observed_at TEXT NOT NULL
            );
            CREATE VIRTUAL TABLE IF NOT EXISTS observations_fts USING fts5(
                summary, content='observations', content_rowid='id'
            );
            CREATE TABLE IF NOT EXISTS actions (
                id INTEGER PRIMARY KEY,
                session_id TEXT NOT NULL REFERENCES sessions(id),
                action_json TEXT NOT NULL,
                outcome TEXT,
                observed_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS skills (
                id INTEGER PRIMARY KEY,
                scope TEXT NOT NULL,
                claim TEXT NOT NULL,
                status TEXT NOT NULL,
                confidence REAL NOT NULL CHECK(confidence BETWEEN 0 AND 1),
                evidence TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS audit_log (
                id INTEGER PRIMARY KEY,
                event TEXT NOT NULL,
                detail TEXT NOT NULL,
                recorded_at TEXT NOT NULL
            );
            """
        )
        self._connection.executescript(
            """
            CREATE TRIGGER IF NOT EXISTS observations_ai AFTER INSERT ON observations BEGIN
                INSERT INTO observations_fts(rowid, summary) VALUES (new.id, new.summary);
            END;
            CREATE TRIGGER IF NOT EXISTS observations_ad AFTER DELETE ON observations BEGIN
                INSERT INTO observations_fts(observations_fts, rowid, summary)
                VALUES ('delete', old.id, old.summary);
            END;
            """
        )
        self._connection.commit()

    def create_session(self, session_id: str, goal: str, window_id: str, started_at: str) -> None:
        self._connection.execute(
            "INSERT INTO sessions(id, goal, window_id, started_at) VALUES (?, ?, ?, ?)",
            (session_id, goal, window_id, started_at),
        )
        self._connection.commit()

    def add_observation(
        self,
        session_id: str,
        frame_hash: str,
        summary: str,
        confidence: float,
        observed_at: str,
    ) -> int:
        cursor = self._connection.execute(
            """
            INSERT INTO observations(session_id, frame_hash, summary, confidence, observed_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (session_id, frame_hash, summary, confidence, observed_at),
        )
        self._connection.commit()
        return int(cursor.lastrowid)

    def search_observations(self, query: str, limit: int = 20) -> list[sqlite3.Row]:
        if limit < 1:
            raise ValueError("limit must be positive")
        rows = self._connection.execute(
            """
            SELECT observations.*
            FROM observations_fts
            JOIN observations ON observations.id = observations_fts.rowid
            WHERE observations_fts MATCH ?
            ORDER BY observations.id DESC
            LIMIT ?
            """,
            (query, limit),
        )
        return rows.fetchall()

    def add_skill(
        self,
        scope: str,
        claim: str,
        status: str,
        confidence: float,
        evidence: str,
    ) -> int:
        cursor = self._connection.execute(
            "INSERT INTO skills(scope, claim, status, confidence, evidence) VALUES (?, ?, ?, ?, ?)",
            (scope, claim, status, confidence, evidence),
        )
        self._connection.commit()
        return int(cursor.lastrowid)
