"""
Activity logging database methods
"""
from typing import Optional, List, Dict, Any
from database.db import Database


class ActivityDB:
    """Activity logging extension for Database"""
    
    def __init__(self, db: Database):
        self.db = db
    
    def log_activity(self, activity_type: str, target_type: str, target_id: int,
                    action: str, content_id: Optional[int] = None,
                    book_id: Optional[int] = None, details: Optional[str] = None) -> int:
        """Log an activity"""
        conn = self.db._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO activity_log (activity_type, target_type, target_id, 
                                        content_id, book_id, action, details)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (activity_type, target_type, target_id, content_id, book_id, action, details))
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()
    
    def get_activities(self, target_type: Optional[str] = None,
                      target_id: Optional[int] = None,
                      limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """Get activities with optional filters"""
        conn = self.db._get_connection()
        try:
            cursor = conn.cursor()
            if target_type and target_id:
                cursor.execute("""
                    SELECT * FROM activity_log 
                    WHERE target_type = ? AND target_id = ?
                    ORDER BY created_at DESC LIMIT ? OFFSET ?
                """, (target_type, target_id, limit, offset))
            elif target_type:
                cursor.execute("""
                    SELECT * FROM activity_log 
                    WHERE target_type = ?
                    ORDER BY created_at DESC LIMIT ? OFFSET ?
                """, (target_type, limit, offset))
            else:
                cursor.execute("""
                    SELECT * FROM activity_log 
                    ORDER BY created_at DESC LIMIT ? OFFSET ?
                """, (limit, offset))
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()
    
    def get_activity_count(self, target_type: Optional[str] = None,
                          target_id: Optional[int] = None) -> int:
        """Get count of activities"""
        conn = self.db._get_connection()
        try:
            cursor = conn.cursor()
            if target_type and target_id:
                cursor.execute("""
                    SELECT COUNT(*) FROM activity_log 
                    WHERE target_type = ? AND target_id = ?
                """, (target_type, target_id))
            elif target_type:
                cursor.execute("""
                    SELECT COUNT(*) FROM activity_log 
                    WHERE target_type = ?
                """, (target_type,))
            else:
                cursor.execute("SELECT COUNT(*) FROM activity_log")
            return cursor.fetchone()[0]
        finally:
            conn.close()

