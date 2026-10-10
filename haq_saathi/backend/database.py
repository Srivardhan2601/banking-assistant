"""
SQLite storage for drafted labour grievance complaints in Haq Saathi.
Contains no government IDs, no bank numbers, and zero private credentials.
"""

import sqlite3
import json
from pathlib import Path
from typing import Optional, List, Dict, Any
import os
import tempfile
from .models import ComplaintRecord

if os.environ.get("VERCEL") or not os.access(Path(__file__).resolve().parent.parent, os.W_OK):
    DB_PATH = Path(tempfile.gettempdir()) / "haq_saathi.db"
else:
    DB_PATH = Path(__file__).resolve().parent.parent / "haq_saathi.db"


class ComplaintDatabase:
    """Lightweight SQLite database for storing generated complaint drafts."""

    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self):
        try:
            conn = sqlite3.connect(str(self.db_path))
        except Exception:
            conn = sqlite3.connect(":memory:")
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS complaints (
                    complaint_id TEXT PRIMARY KEY,
                    created_at TEXT NOT NULL,
                    language TEXT NOT NULL,
                    worker_name TEXT,
                    worker_category TEXT NOT NULL,
                    employer_name TEXT NOT NULL,
                    work_location TEXT,
                    district TEXT NOT NULL,
                    unpaid_period TEXT,
                    amount_owed TEXT,
                    description TEXT,
                    desired_relief TEXT,
                    rights_violated TEXT,
                    source_citation TEXT,
                    routed_office_id TEXT,
                    routed_office_name TEXT,
                    routed_office_address TEXT,
                    phone TEXT,
                    raw_data TEXT
                )
            """)
            conn.commit()

    def save_complaint(self, record: ComplaintRecord) -> str:
        with self._get_connection() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO complaints (
                    complaint_id, created_at, language, worker_name, worker_category,
                    employer_name, work_location, district, unpaid_period, amount_owed,
                    description, desired_relief, rights_violated, source_citation,
                    routed_office_id, routed_office_name, routed_office_address, phone, raw_data
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                record.complaint_id,
                record.created_at,
                record.language,
                record.worker_name,
                record.worker_category,
                record.employer_name,
                record.work_location,
                record.district,
                record.unpaid_period,
                record.amount_owed,
                record.description,
                record.desired_relief,
                record.rights_violated,
                record.source_citation,
                record.routed_office_id,
                record.routed_office_name,
                record.routed_office_address,
                record.phone,
                json.dumps(record.model_dump())
            ))
            conn.commit()
        return record.complaint_id

    def get_complaint(self, complaint_id: str) -> Optional[ComplaintRecord]:
        with self._get_connection() as conn:
            cur = conn.execute("SELECT raw_data FROM complaints WHERE complaint_id = ?", (complaint_id,))
            row = cur.fetchone()
            if row and row["raw_data"]:
                data = json.loads(row["raw_data"])
                return ComplaintRecord(**data)
        return None

    def list_recent_complaints(self, limit: int = 20) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cur = conn.execute("SELECT complaint_id, created_at, worker_category, district, amount_owed, routed_office_name FROM complaints ORDER BY created_at DESC LIMIT ?", (limit,))
            return [dict(r) for r in cur.fetchall()]


db = ComplaintDatabase()
