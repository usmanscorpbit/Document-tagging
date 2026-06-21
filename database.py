import sqlite3
import json
from datetime import datetime

DB_PATH = 'documents.db'

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            filepath TEXT NOT NULL,
            file_size INTEGER,
            tags TEXT,
            upload_date TEXT,
            word_count INTEGER DEFAULT 0,
            category TEXT DEFAULT 'General'
        )
    ''')
    # Add new columns to existing DB if they don't exist yet
    for col, definition in [('word_count', 'INTEGER DEFAULT 0'), ('category', "TEXT DEFAULT 'General'")]:
        try:
            c.execute(f'ALTER TABLE documents ADD COLUMN {col} {definition}')
        except Exception:
            pass
    conn.commit()
    conn.close()

def save_document(filename, filepath, file_size, tags, word_count=0, category='General'):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        INSERT INTO documents (filename, filepath, file_size, tags, upload_date, word_count, category)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (filename, filepath, file_size, json.dumps(tags), datetime.now().strftime('%Y-%m-%d %H:%M'), word_count, category))
    doc_id = c.lastrowid
    conn.commit()
    conn.close()
    return doc_id

def get_document(doc_id):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM documents WHERE id = ?', (doc_id,))
    row = c.fetchone()
    conn.close()
    if row:
        doc = dict(row)
        doc['tags'] = json.loads(doc['tags'])
        return doc
    return None

def get_all_documents():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM documents ORDER BY id DESC')
    rows = c.fetchall()
    conn.close()
    docs = []
    for row in rows:
        doc = dict(row)
        doc['tags'] = json.loads(doc['tags'])
        docs.append(doc)
    return docs

def update_tags(doc_id, tags):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('UPDATE documents SET tags = ? WHERE id = ?', (json.dumps(tags), doc_id))
    conn.commit()
    conn.close()

def delete_document(doc_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('DELETE FROM documents WHERE id = ?', (doc_id,))
    conn.commit()
    conn.close()
