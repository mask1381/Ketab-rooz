-- database/schema.sql

CREATE TABLE IF NOT EXISTS books (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    author TEXT,
    pdf_file_id TEXT NOT NULL,
    pdf_message_id INTEGER NOT NULL,
    cover_file_id TEXT,
    cover_message_id INTEGER,
    category TEXT,
    tags TEXT,
    total_pages INTEGER,
    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT 'pending',
    processed_date TIMESTAMP,
    notes TEXT
);

CREATE TABLE IF NOT EXISTS content (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id INTEGER,
    type TEXT NOT NULL,
    text TEXT,
    file_id TEXT,
    message_id INTEGER,
    caption TEXT,
    status TEXT DEFAULT 'draft',
    is_manual BOOLEAN DEFAULT 0,
    use_cover BOOLEAN DEFAULT 0,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    approved_date TIMESTAMP,
    publish_date TIMESTAMP,
    published_date TIMESTAMP,
    published_message_id INTEGER,
    views INTEGER DEFAULT 0,
    reactions INTEGER DEFAULT 0,
    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    type TEXT NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS schedule_pattern (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    day_of_week INTEGER,
    time TEXT,
    content_types TEXT,
    posts_count INTEGER DEFAULT 1,
    is_active BOOLEAN DEFAULT 1
);

CREATE TABLE IF NOT EXISTS hashtags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tag TEXT NOT NULL UNIQUE,
    tag_type TEXT DEFAULT 'general',
    count INTEGER DEFAULT 1,
    is_approved BOOLEAN DEFAULT 0,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    approved_date TIMESTAMP
);

CREATE TABLE IF NOT EXISTS footer_settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    setting_key TEXT NOT NULL UNIQUE,
    setting_value TEXT,
    is_active BOOLEAN DEFAULT 1,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Default settings
INSERT OR IGNORE INTO settings (key, value, type, updated_at) VALUES 
('ai_model', 'google/gemini-2.0-flash-exp:free', 'string', CURRENT_TIMESTAMP),
('quote_count', '5', 'integer', CURRENT_TIMESTAMP),
('summary_length_min', '150', 'integer', CURRENT_TIMESTAMP),
('summary_length_max', '300', 'integer', CURRENT_TIMESTAMP),
('design_template', 'modern', 'string', CURRENT_TIMESTAMP),
('font_size', '60', 'integer', CURRENT_TIMESTAMP),
('bg_color', '#1a1a2e', 'string', CURRENT_TIMESTAMP),
('hashtag_enabled', '1', 'boolean', CURRENT_TIMESTAMP),
('footer_enabled', '1', 'boolean', CURRENT_TIMESTAMP),
('footer_show_id', '1', 'boolean', CURRENT_TIMESTAMP),
('footer_template', 'ID: {content_id}', 'string', CURRENT_TIMESTAMP);

-- Default footer settings
INSERT OR IGNORE INTO footer_settings (setting_key, setting_value, is_active) VALUES 
('show_content_id', '1', 1),
('id_format', 'ID: {id}', 1),
('custom_text', '', 1);

-- Activity tracking table for tracking work done on channels and groups
CREATE TABLE IF NOT EXISTS activity_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    activity_type TEXT NOT NULL,
    target_type TEXT NOT NULL,
    target_id INTEGER NOT NULL,
    content_id INTEGER,
    book_id INTEGER,
    action TEXT NOT NULL,
    details TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (content_id) REFERENCES content(id) ON DELETE SET NULL,
    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE SET NULL
);
