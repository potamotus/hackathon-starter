from __future__ import annotations

import sqlite3


MEMORY_COLUMNS = {
    "category": "TEXT DEFAULT 'project'",
    "confidence": "REAL DEFAULT 0.8",
    "source": "TEXT DEFAULT 'auto_extract'",
    "last_accessed": "TEXT",
    "access_count": "INTEGER DEFAULT 0",
    "source_chat_id": "TEXT DEFAULT ''",
    "scope": "TEXT DEFAULT 'personal'",
    "status": "TEXT DEFAULT 'active'",
    "superseded_by": "TEXT DEFAULT ''",
    "metadata": "TEXT DEFAULT '{}'",
}


CREATE_STATEMENTS = [
    """
    CREATE TABLE IF NOT EXISTS gpthub_document (
        id TEXT PRIMARY KEY,
        owner_user_id TEXT DEFAULT '',
        workspace_id TEXT DEFAULT '',
        organization_id TEXT DEFAULT '',
        scope TEXT NOT NULL DEFAULT 'project',
        title TEXT NOT NULL,
        mime_type TEXT DEFAULT '',
        source_kind TEXT DEFAULT 'upload',
        storage_path TEXT DEFAULT '',
        checksum TEXT DEFAULT '',
        version INTEGER DEFAULT 1,
        status TEXT NOT NULL DEFAULT 'active',
        source_chat_id TEXT DEFAULT '',
        full_text TEXT DEFAULT '',
        metadata TEXT NOT NULL DEFAULT '{}',
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS gpthub_document_chunk (
        id TEXT PRIMARY KEY,
        document_id TEXT NOT NULL,
        chunk_index INTEGER NOT NULL,
        section_key TEXT DEFAULT '',
        content TEXT NOT NULL,
        token_count INTEGER DEFAULT 0,
        char_count INTEGER DEFAULT 0,
        embedding_ref TEXT DEFAULT '',
        metadata TEXT NOT NULL DEFAULT '{}',
        created_at TEXT NOT NULL,
        FOREIGN KEY(document_id) REFERENCES gpthub_document(id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS gpthub_document_fact (
        id TEXT PRIMARY KEY,
        document_id TEXT NOT NULL,
        scope TEXT NOT NULL DEFAULT 'project',
        fact_type TEXT NOT NULL,
        normalized_fact TEXT DEFAULT '',
        content TEXT NOT NULL,
        confidence REAL DEFAULT 0.8,
        pii_class TEXT DEFAULT 'none',
        is_critical INTEGER DEFAULT 0,
        source_span TEXT DEFAULT '',
        metadata TEXT NOT NULL DEFAULT '{}',
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        FOREIGN KEY(document_id) REFERENCES gpthub_document(id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS gpthub_knowledge_promotion (
        id TEXT PRIMARY KEY,
        source_scope TEXT NOT NULL,
        target_scope TEXT NOT NULL,
        source_type TEXT NOT NULL,
        source_id TEXT NOT NULL,
        approved_by TEXT DEFAULT '',
        reason TEXT DEFAULT '',
        metadata TEXT NOT NULL DEFAULT '{}',
        created_at TEXT NOT NULL
    )
    """,
]


INDEX_STATEMENTS = [
    "CREATE INDEX IF NOT EXISTS idx_memory_user_scope_status ON memory(user_id, scope, status)",
    "CREATE INDEX IF NOT EXISTS idx_memory_normalized_fact ON memory(user_id, scope, category, status)",
    "CREATE INDEX IF NOT EXISTS idx_document_scope_workspace ON gpthub_document(scope, workspace_id, organization_id, status)",
    "CREATE INDEX IF NOT EXISTS idx_document_checksum ON gpthub_document(checksum)",
    "CREATE INDEX IF NOT EXISTS idx_chunk_document ON gpthub_document_chunk(document_id, chunk_index)",
    "CREATE INDEX IF NOT EXISTS idx_fact_document ON gpthub_document_fact(document_id, fact_type)",
    "CREATE INDEX IF NOT EXISTS idx_fact_scope_norm ON gpthub_document_fact(scope, normalized_fact, is_critical)",
    "CREATE INDEX IF NOT EXISTS idx_promotion_target ON gpthub_knowledge_promotion(target_scope, source_type, source_id)",
]


def ensure_layered_storage_schema(db_path: str) -> None:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    c.execute("PRAGMA table_info(memory)")
    cols = {row["name"] for row in c.fetchall()}
    for col, dtype in MEMORY_COLUMNS.items():
        if col not in cols:
            c.execute(f"ALTER TABLE memory ADD COLUMN {col} {dtype}")

    for stmt in CREATE_STATEMENTS:
        c.execute(stmt)

    for stmt in INDEX_STATEMENTS:
        c.execute(stmt)

    conn.commit()
    conn.close()
