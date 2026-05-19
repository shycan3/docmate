import json
import os
import sqlite3
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional, List


class AnalysisStorage:
    """Simple SQLite-based storage for analysis results."""

    def __init__(self, db_path: str = "docmate.db"):
        self.db_path = db_path
        self.connection = None
        self._init_db()

    def _init_db(self):
        """Create tables if they don't exist."""
        # For in-memory databases, keep the connection open
        if self.db_path == ":memory:":
            self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
            conn = self.connection
        else:
            conn = sqlite3.connect(self.db_path)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS analyses (
                id TEXT PRIMARY KEY,
                created_at TEXT NOT NULL,
                filename TEXT NOT NULL,
                document_text TEXT,
                profile TEXT,
                extraction TEXT,
                eligibility TEXT,
                warnings TEXT,
                checklist TEXT,
                actions TEXT
            )
        """)
        conn.commit()

        if self.db_path != ":memory:":
            conn.close()

    def save(
        self,
        filename: str,
        document_text: str,
        profile: dict,
        extraction: dict,
        eligibility: dict,
        warnings: list,
        checklist: list,
        actions: list,
    ) -> str:
        """
        Save analysis result and return the ID.

        Args:
            filename: Name of the analyzed document
            document_text: Full text of the document
            profile: User profile dict
            extraction: Extracted fields dict
            eligibility: Eligibility result dict
            warnings: List of warning dicts
            checklist: List of checklist item dicts
            actions: List of action dicts

        Returns:
            str: UUID of the saved analysis
        """
        analysis_id = str(uuid.uuid4())
        created_at = datetime.utcnow().isoformat() + "Z"

        if self.db_path == ":memory:":
            conn = self.connection
            should_close = False
        else:
            conn = sqlite3.connect(self.db_path)
            should_close = True

        try:
            conn.execute(
                """
                INSERT INTO analyses 
                (id, created_at, filename, document_text, profile, 
                 extraction, eligibility, warnings, checklist, actions)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    analysis_id,
                    created_at,
                    filename,
                    document_text,
                    json.dumps(profile, ensure_ascii=False),
                    json.dumps(extraction, ensure_ascii=False),
                    json.dumps(eligibility, ensure_ascii=False),
                    json.dumps(warnings, ensure_ascii=False),
                    json.dumps(checklist, ensure_ascii=False),
                    json.dumps(actions, ensure_ascii=False),
                ),
            )
            conn.commit()
        finally:
            if should_close:
                conn.close()

        return analysis_id

    def get(self, analysis_id: str) -> Optional[dict]:
        """Retrieve a single analysis by ID."""
        if self.db_path == ":memory:":
            conn = self.connection
            should_close = False
        else:
            conn = sqlite3.connect(self.db_path)
            should_close = True

        try:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM analyses WHERE id = ?", (analysis_id,)
            )
            row = cursor.fetchone()
        finally:
            if should_close:
                conn.close()

        if not row:
            return None

        return self._row_to_dict(row)

    def list_all(self, limit: int = 50) -> List[dict]:
        """Retrieve all analyses, ordered by creation date (newest first)."""
        if self.db_path == ":memory:":
            conn = self.connection
            should_close = False
        else:
            conn = sqlite3.connect(self.db_path)
            should_close = True

        try:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM analyses ORDER BY created_at DESC LIMIT ?", (limit,)
            )
            rows = cursor.fetchall()
        finally:
            if should_close:
                conn.close()

        return [self._row_to_dict(row) for row in rows]

    def delete(self, analysis_id: str) -> bool:
        """Delete an analysis by ID. Returns True if deleted, False if not found."""
        if self.db_path == ":memory:":
            conn = self.connection
            should_close = False
        else:
            conn = sqlite3.connect(self.db_path)
            should_close = True

        try:
            cursor = conn.execute(
                "DELETE FROM analyses WHERE id = ?", (analysis_id,)
            )
            conn.commit()
            return cursor.rowcount > 0
        finally:
            if should_close:
                conn.close()

    def _row_to_dict(self, row: sqlite3.Row) -> dict:
        """Convert SQL row to dictionary with parsed JSON fields."""
        return {
            "id": row["id"],
            "created_at": row["created_at"],
            "filename": row["filename"],
            "document_text": row["document_text"],
            "profile": json.loads(row["profile"] or "{}"),
            "extraction": json.loads(row["extraction"] or "{}"),
            "eligibility": json.loads(row["eligibility"] or "{}"),
            "warnings": json.loads(row["warnings"] or "[]"),
            "checklist": json.loads(row["checklist"] or "[]"),
            "actions": json.loads(row["actions"] or "[]"),
        }

    def clear_all(self):
        """Clear all analyses (for testing only)."""
        if self.db_path == ":memory:":
            conn = self.connection
            should_close = False
        else:
            conn = sqlite3.connect(self.db_path)
            should_close = True

        try:
            conn.execute("DELETE FROM analyses")
            conn.commit()
        finally:
            if should_close:
                conn.close()


# Global storage instance
_storage_instance: Optional[AnalysisStorage] = None


def get_storage(db_path: str | None = None) -> AnalysisStorage:
    """Get or create the global storage instance."""
    global _storage_instance
    db_path = db_path or os.environ.get("DOCMATE_DB_PATH", "docmate.db")
    if _storage_instance is None or _storage_instance.db_path != db_path:
        _storage_instance = AnalysisStorage(db_path)
    return _storage_instance
