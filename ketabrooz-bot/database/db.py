"""
Database manager for KetabeRooz bot
"""
import sqlite3
import os
from typing import Optional, List, Dict, Any
from datetime import datetime


class Database:
    """SQLite database manager"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._ensure_db_dir()
        self.init()
    
    def _ensure_db_dir(self):
        """Ensure database directory exists"""
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
    
    def _get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init(self):
        """Initialize database with schema"""
        schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
        
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema = f.read()
        
        conn = self._get_connection()
        try:
            conn.executescript(schema)
            conn.commit()
        finally:
            conn.close()
    
    # Books operations
    def add_book(self, title: str, pdf_file_id: str, pdf_message_id: int, 
                 author: Optional[str] = None, category: Optional[str] = None,
                 tags: Optional[str] = None, total_pages: Optional[int] = None,
                 cover_file_id: Optional[str] = None, cover_message_id: Optional[int] = None,
                 status: str = 'pending') -> int:
        """Add a new book to database"""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO books (title, author, pdf_file_id, pdf_message_id, 
                                 category, tags, total_pages, cover_file_id, 
                                 cover_message_id, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (title, author, pdf_file_id, pdf_message_id, category, tags, 
                  total_pages, cover_file_id, cover_message_id, status))
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()
    
    def get_book(self, book_id: int) -> Optional[Dict[str, Any]]:
        """Get book by ID"""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM books WHERE id = ?", (book_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    def get_book_by_file_id(self, pdf_file_id: str) -> Optional[Dict[str, Any]]:
        """Get book by PDF file ID"""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM books WHERE pdf_file_id = ?", (pdf_file_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()
    
    def get_all_books(self, status: Optional[str] = None, 
                     limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """Get all books with optional status filter"""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            if status:
                cursor.execute("""
                    SELECT * FROM books WHERE status = ? 
                    ORDER BY upload_date DESC LIMIT ? OFFSET ?
                """, (status, limit, offset))
            else:
                cursor.execute("""
                    SELECT * FROM books ORDER BY upload_date DESC 
                    LIMIT ? OFFSET ?
                """, (limit, offset))
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()
    
    def update_book(self, book_id: int, **kwargs):
        """Update book fields"""
        if not kwargs:
            return
        
        allowed_fields = ['title', 'author', 'cover_file_id', 'cover_message_id',
                         'category', 'tags', 'total_pages', 'status', 
                         'processed_date', 'notes']
        
        updates = []
        values = []
        for key, value in kwargs.items():
            if key in allowed_fields:
                updates.append(f"{key} = ?")
                values.append(value)
        
        if not updates:
            return
        
        values.append(book_id)
        query = f"UPDATE books SET {', '.join(updates)} WHERE id = ?"
        
        conn = self._get_connection()
        try:
            conn.execute(query, values)
            conn.commit()
        finally:
            conn.close()
    
    # Content operations
    def add_content(self, book_id: Optional[int] = None, content_type: str = 'text', 
                   text: Optional[str] = None, file_id: Optional[str] = None, 
                   message_id: Optional[int] = None, caption: Optional[str] = None, 
                   is_manual: bool = False, use_cover: bool = False, 
                   status: str = 'draft') -> int:
        """Add new content"""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO content (book_id, type, text, file_id, message_id, 
                                   caption, is_manual, use_cover, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (book_id, content_type, text, file_id, message_id, caption, 
                  is_manual, use_cover, status))
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()
    
    def get_content(self, content_id: int) -> Optional[Dict[str, Any]]:
        """Get content by ID"""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM content WHERE id = ?", (content_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()
    
    def get_content_by_status(self, status: str = '', limit: int = 50, 
                             offset: int = 0) -> List[Dict[str, Any]]:
        """Get content by status (empty string returns all)"""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            if status:
                cursor.execute("""
                    SELECT c.*, b.title as book_title, b.author as book_author
                    FROM content c
                    LEFT JOIN books b ON c.book_id = b.id
                    WHERE c.status = ?
                    ORDER BY c.created_date DESC
                    LIMIT ? OFFSET ?
                """, (status, limit, offset))
            else:
                cursor.execute("""
                    SELECT c.*, b.title as book_title, b.author as book_author
                    FROM content c
                    LEFT JOIN books b ON c.book_id = b.id
                    ORDER BY c.created_date DESC
                    LIMIT ? OFFSET ?
                """, (limit, offset))
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()
    
    def get_content_count_by_status(self, status: str) -> int:
        """Get count of content by status"""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) as count FROM content WHERE status = ?", (status,))
            row = cursor.fetchone()
            return row['count'] if row else 0
        finally:
            conn.close()
    
    def update_content(self, content_id: int, **kwargs):
        """Update content fields"""
        if not kwargs:
            return
        
        allowed_fields = ['text', 'file_id', 'message_id', 'caption', 'status',
                         'approved_date', 'publish_date', 'published_date',
                         'published_message_id', 'use_cover']
        
        updates = []
        values = []
        for key, value in kwargs.items():
            if key in allowed_fields:
                updates.append(f"{key} = ?")
                values.append(value)
        
        if not updates:
            return
        
        values.append(content_id)
        query = f"UPDATE content SET {', '.join(updates)} WHERE id = ?"
        
        conn = self._get_connection()
        try:
            conn.execute(query, values)
            conn.commit()
        finally:
            conn.close()
    
    # Settings operations
    def get_setting(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Get setting value"""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
            row = cursor.fetchone()
            return row['value'] if row else default
        finally:
            conn.close()
    
    def set_setting(self, key: str, value: str, setting_type: str = 'string'):
        """Set setting value"""
        conn = self._get_connection()
        try:
            conn.execute("""
                INSERT OR REPLACE INTO settings (key, value, type, updated_at)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            """, (key, value, setting_type))
            conn.commit()
        finally:
            conn.close()
    
    def get_all_settings(self) -> Dict[str, Dict[str, Any]]:
        """Get all settings"""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM settings")
            settings = {}
            for row in cursor.fetchall():
                settings[row['key']] = {
                    'value': row['value'],
                    'type': row['type']
                }
            return settings
        finally:
            conn.close()
    
    # Schedule operations
    def add_schedule_pattern(self, day_of_week: int, time: str, 
                            content_types: str, posts_count: int = 1) -> int:
        """Add schedule pattern"""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO schedule_pattern (day_of_week, time, content_types, posts_count)
                VALUES (?, ?, ?, ?)
            """, (day_of_week, time, content_types, posts_count))
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()
    
    def get_schedule_patterns(self, is_active: bool = True) -> List[Dict[str, Any]]:
        """Get schedule patterns"""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM schedule_pattern 
                WHERE is_active = ?
                ORDER BY day_of_week, time
            """, (is_active,))
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()
    
    # Hashtag operations
    def add_hashtag(self, tag: str, tag_type: str = 'general', count: int = 1) -> int:
        """Add a new hashtag"""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            # Remove # if exists
            tag = tag.replace('#', '').strip()
            cursor.execute("""
                INSERT OR IGNORE INTO hashtags (tag, tag_type, count, is_approved)
                VALUES (?, ?, ?, 0)
            """, (tag, tag_type, count))
            conn.commit()
            # Get the ID
            cursor.execute("SELECT id FROM hashtags WHERE tag = ?", (tag,))
            row = cursor.fetchone()
            return row['id'] if row else 0
        finally:
            conn.close()
    
    def get_hashtag(self, tag_id: int) -> Optional[Dict[str, Any]]:
        """Get hashtag by ID"""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM hashtags WHERE id = ?", (tag_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()
    
    def get_all_hashtags(self, is_approved: Optional[bool] = None, 
                         tag_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all hashtags with optional filters"""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            query = "SELECT * FROM hashtags WHERE 1=1"
            params = []
            
            if is_approved is not None:
                query += " AND is_approved = ?"
                params.append(1 if is_approved else 0)
            
            if tag_type:
                query += " AND tag_type = ?"
                params.append(tag_type)
            
            query += " ORDER BY created_date DESC"
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()
    
    def approve_hashtag(self, tag_id: int):
        """Approve a hashtag"""
        conn = self._get_connection()
        try:
            conn.execute("""
                UPDATE hashtags 
                SET is_approved = 1, approved_date = CURRENT_TIMESTAMP 
                WHERE id = ?
            """, (tag_id,))
            conn.commit()
        finally:
            conn.close()
    
    def update_hashtag(self, tag_id: int, **kwargs):
        """Update hashtag fields"""
        if not kwargs:
            return
        
        allowed_fields = ['tag', 'tag_type', 'count', 'is_approved']
        updates = []
        values = []
        for key, value in kwargs.items():
            if key in allowed_fields:
                updates.append(f"{key} = ?")
                values.append(value)
        
        if not updates:
            return
        
        values.append(tag_id)
        query = f"UPDATE hashtags SET {', '.join(updates)} WHERE id = ?"
        
        conn = self._get_connection()
        try:
            conn.execute(query, values)
            conn.commit()
        finally:
            conn.close()
    
    def delete_hashtag(self, tag_id: int):
        """Delete a hashtag"""
        conn = self._get_connection()
        try:
            conn.execute("DELETE FROM hashtags WHERE id = ?", (tag_id,))
            conn.commit()
        finally:
            conn.close()
    
    def get_approved_hashtags_by_type(self, tag_type: str, count: int = 5) -> List[str]:
        """Get approved hashtags by type"""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT tag FROM hashtags 
                WHERE is_approved = 1 AND tag_type = ?
                ORDER BY count DESC, created_date DESC
                LIMIT ?
            """, (tag_type, count))
            return [row['tag'] for row in cursor.fetchall()]
        finally:
            conn.close()
    
    # Footer settings operations
    def get_footer_setting(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Get footer setting value"""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT setting_value FROM footer_settings 
                WHERE setting_key = ? AND is_active = 1
            """, (key,))
            row = cursor.fetchone()
            return row['setting_value'] if row else default
        finally:
            conn.close()
    
    def set_footer_setting(self, key: str, value: str):
        """Set footer setting value"""
        conn = self._get_connection()
        try:
            conn.execute("""
                INSERT OR REPLACE INTO footer_settings (setting_key, setting_value, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
            """, (key, value))
            conn.commit()
        finally:
            conn.close()
    
    def get_all_footer_settings(self) -> Dict[str, Any]:
        """Get all footer settings"""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM footer_settings WHERE is_active = 1")
            settings = {}
            for row in cursor.fetchall():
                settings[row['setting_key']] = row['setting_value']
            return settings
        finally:
            conn.close()
    
    # Statistics
    def get_stats(self) -> Dict[str, Any]:
        """Get bot statistics"""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            stats = {}
            
            # Books stats
            cursor.execute("SELECT COUNT(*) as count FROM books")
            stats['total_books'] = cursor.fetchone()['count']
            
            cursor.execute("SELECT COUNT(*) as count FROM books WHERE status = 'processed'")
            stats['processed_books'] = cursor.fetchone()['count']
            
            # Content stats
            cursor.execute("SELECT COUNT(*) as count FROM content")
            stats['total_content'] = cursor.fetchone()['count']
            
            cursor.execute("SELECT COUNT(*) as count FROM content WHERE status = 'approved'")
            stats['approved_content'] = cursor.fetchone()['count']
            
            cursor.execute("SELECT COUNT(*) as count FROM content WHERE status = 'published'")
            stats['published_content'] = cursor.fetchone()['count']
            
            # Hashtag stats
            cursor.execute("SELECT COUNT(*) as count FROM hashtags")
            stats['total_hashtags'] = cursor.fetchone()['count']
            
            cursor.execute("SELECT COUNT(*) as count FROM hashtags WHERE is_approved = 1")
            stats['approved_hashtags'] = cursor.fetchone()['count']
            
            return stats
        finally:
            conn.close()

