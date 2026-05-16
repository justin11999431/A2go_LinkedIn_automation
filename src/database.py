"""Database management for lead state persistence."""

import sqlite3
import json
import os
import logging
from typing import Optional, Dict, Any
from datetime import datetime
from src.models import SequenceState

logger = logging.getLogger(__name__)

class StateDatabase:
    """SQLite database for persisting lead sequence state."""
    
    def __init__(self, db_path: str = "data/automation.db"):
        """Initialize database connection.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        # Ensure data directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self._init_db()
    
    def _get_connection(self):
        return sqlite3.connect(self.db_path)
    
    def close(self):
        """Close the database (no-op as connections are per-method)."""
        pass

    def _init_db(self):
        """Create tables if they don't exist."""
        conn = self._get_connection()
        try:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS sequence_state (
                    lead_id TEXT PRIMARY KEY,
                    email TEXT,
                    phone TEXT,
                    current_email_step INTEGER DEFAULT 0,
                    current_linkedin_step INTEGER DEFAULT 0,
                    email_status TEXT DEFAULT 'pending',
                    linkedin_status TEXT DEFAULT 'pending',
                    sms_status TEXT DEFAULT 'pending',
                    last_interaction_at TEXT,
                    is_paused INTEGER DEFAULT 0,
                    pause_reason TEXT,
                    next_step_due_at TEXT,
                    metadata TEXT,
                    updated_at TEXT
                )
            """)
            # Migration check
            cursor = conn.execute("PRAGMA table_info(sequence_state)")
            columns = [col[1] for col in cursor.fetchall()]
            if 'email' not in columns:
                conn.execute("ALTER TABLE sequence_state ADD COLUMN email TEXT")
            if 'phone' not in columns:
                conn.execute("ALTER TABLE sequence_state ADD COLUMN phone TEXT")
            if 'current_linkedin_step' not in columns:
                conn.execute("ALTER TABLE sequence_state ADD COLUMN current_linkedin_step INTEGER DEFAULT 0")
            
            conn.commit()
        finally:
            conn.close()
            
    def upsert_state(self, state: SequenceState):
        """Insert or update sequence state.
        
        Args:
            state: SequenceState object
        """
        conn = self._get_connection()
        try:
            conn.execute("""
                INSERT INTO sequence_state (
                    lead_id, email, phone, current_email_step, current_linkedin_step,
                    email_status, linkedin_status, sms_status,
                    last_interaction_at, is_paused, pause_reason, next_step_due_at, metadata, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(lead_id) DO UPDATE SET
                    email=excluded.email,
                    phone=excluded.phone,
                    current_email_step=excluded.current_email_step,
                    current_linkedin_step=excluded.current_linkedin_step,
                    email_status=excluded.email_status,
                    linkedin_status=excluded.linkedin_status,
                    sms_status=excluded.sms_status,
                    last_interaction_at=excluded.last_interaction_at,
                    is_paused=excluded.is_paused,
                    pause_reason=excluded.pause_reason,
                    next_step_due_at=excluded.next_step_due_at,
                    metadata=excluded.metadata,
                    updated_at=excluded.updated_at
            """, (
                state.lead_id,
                state.email,
                state.phone,
                state.current_email_step,
                state.current_linkedin_step,
                state.email_status,
                state.linkedin_status,
                state.sms_status,
                state.last_interaction_at.isoformat() if state.last_interaction_at else None,
                1 if state.is_paused else 0,
                state.pause_reason,
                state.next_step_due_at.isoformat() if state.next_step_due_at else None,
                json.dumps(state.metadata),
                datetime.now().isoformat()
            ))
            conn.commit()
        finally:
            conn.close()
            
    def get_state(self, lead_id: str) -> Optional[SequenceState]:
        """Retrieve sequence state for a lead.
        
        Args:
            lead_id: Unique lead identifier
            
        Returns:
            SequenceState object or None
        """
        conn = self._get_connection()
        try:
            cursor = conn.execute("SELECT * FROM sequence_state WHERE lead_id = ?", (lead_id,))
            row = cursor.fetchone()
            
            if not row:
                return None
            
            # Table schema order: lead_id, email, phone, current_email_step, current_linkedin_step, ...
            return SequenceState(
                lead_id=row[0],
                email=row[1] or "",
                phone=row[2],
                current_email_step=row[3],
                current_linkedin_step=row[4],
                email_status=row[5],
                linkedin_status=row[6],
                sms_status=row[7],
                last_interaction_at=datetime.fromisoformat(row[8]) if row[8] else None,
                is_paused=bool(row[9]),
                pause_reason=row[10],
                next_step_due_at=datetime.fromisoformat(row[11]) if row[11] else None,
                metadata=json.loads(row[12]) if row[12] else {}
            )
        finally:
            conn.close()

    def get_state_by_email(self, email: str) -> Optional[SequenceState]:
        """Retrieve sequence state for a lead by email.
        
        Args:
            email: Lead's email address
            
        Returns:
            SequenceState object or None
        """
        conn = self._get_connection()
        try:
            cursor = conn.execute("SELECT * FROM sequence_state WHERE email = ?", (email,))
            row = cursor.fetchone()
            
            if not row:
                return None
            
            return SequenceState(
                lead_id=row[0],
                email=row[1] or "",
                phone=row[2],
                current_email_step=row[3],
                current_linkedin_step=row[4],
                email_status=row[5],
                linkedin_status=row[6],
                sms_status=row[7],
                last_interaction_at=datetime.fromisoformat(row[8]) if row[8] else None,
                is_paused=bool(row[9]),
                pause_reason=row[10],
                next_step_due_at=datetime.fromisoformat(row[11]) if row[11] else None,
                metadata=json.loads(row[12]) if row[12] else {}
            )
        finally:
            conn.close()

    def get_state_by_phone(self, phone: str) -> Optional[SequenceState]:
        """Retrieve sequence state for a lead by phone.
        
        Args:
            phone: Lead's phone number
            
        Returns:
            SequenceState object or None
        """
        conn = self._get_connection()
        try:
            # Simple phone matching (may need normalization)
            cursor = conn.execute("SELECT * FROM sequence_state WHERE phone LIKE ?", (f'%{phone}%',))
            row = cursor.fetchone()
            
            if not row:
                return None
            
            return SequenceState(
                lead_id=row[0],
                email=row[1] or "",
                phone=row[2],
                current_email_step=row[3],
                current_linkedin_step=row[4],
                email_status=row[5],
                linkedin_status=row[6],
                sms_status=row[7],
                last_interaction_at=datetime.fromisoformat(row[8]) if row[8] else None,
                is_paused=bool(row[9]),
                pause_reason=row[10],
                next_step_due_at=datetime.fromisoformat(row[11]) if row[11] else None,
                metadata=json.loads(row[12]) if row[12] else {}
            )
        finally:
            conn.close()
