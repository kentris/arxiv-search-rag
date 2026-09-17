-- Enable foreign key constraints in SQLite
PRAGMA foreign_keys = ON;

-- 1. Papers Table
CREATE TABLE IF NOT EXISTS papers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    arxiv_id TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    published_date TEXT, -- Stored as ISO8601 string 'YYYY-MM-DD'
    category TEXT NOT NULL,
    url TEXT NOT NULL,

    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 2. Paper Sections Table
CREATE TABLE IF NOT EXISTS paper_sections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    paper_id INTEGER NOT NULL,

    section_number INTEGER NOT NULL,
    title TEXT NOT NULL,
    text TEXT NOT NULL,
    tfidf_vector TEXT, -- Stores JSON stringified array e.g., "[0.0, 0.12, ...]"

    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (paper_id) REFERENCES papers(id) ON DELETE CASCADE,
    UNIQUE (paper_id, section_number)
);

-- 3. Indexes
CREATE INDEX IF NOT EXISTS idx_papers_category
    ON papers(category);

CREATE INDEX IF NOT EXISTS idx_paper_sections_paper_id
    ON paper_sections(paper_id);