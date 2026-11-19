
import sqlite3
import numpy as np


def create_database(db_path="smartcache.db"):

    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cache (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT NOT NULL,
            answer TEXT NOT NULL,
            embedding BLOB NOT NULL
        )
    """)

    # Add timestamp column to existing databases if needed
    cursor.execute("PRAGMA table_info(cache)")
    columns = [column[1] for column in cursor.fetchall()]

    if "created_at" not in columns:

        cursor.execute("""
            ALTER TABLE cache
            ADD COLUMN created_at TEXT
        """)

        # Add timestamps to existing records
        cursor.execute("""
            UPDATE cache
            SET created_at = datetime('now', '+5 hours', '+30 minutes')
            WHERE created_at IS NULL
        """)

    connection.commit()
    connection.close()


def save_cache(question, answer, embedding, db_path="smartcache.db"):

    embedding_array = embedding.cpu().numpy().astype(np.float32)
    embedding_bytes = embedding_array.tobytes()

    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    cursor.execute("""
        SELECT id FROM cache
        WHERE LOWER(TRIM(question)) = LOWER(TRIM(?))
    """, (question,))

    existing_entry = cursor.fetchone()

    if existing_entry:
        connection.close()
        return False

    cursor.execute("""
        INSERT INTO cache (
            question,
            answer,
            embedding,
            created_at
        )
        VALUES (?, ?, ?, CURRENT_TIMESTAMP)
    """, (question, answer, embedding_bytes))

    connection.commit()
    connection.close()

    return True


def get_all_cache(db_path="smartcache.db"):

    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    cursor.execute("""
        SELECT question, answer, embedding, created_at
        FROM cache
    """)

    rows = cursor.fetchall()
    connection.close()

    cache_entries = []

    for question, answer, embedding_bytes, created_at in rows:

        embedding_array = np.frombuffer(
            embedding_bytes,
            dtype=np.float32
        ).copy()

        cache_entries.append({
            "question": question,
            "answer": answer,
            "embedding": embedding_array,
            "created_at": created_at
        })

    return cache_entries


def delete_cache(question, db_path="smartcache.db"):

    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    cursor.execute("""
        DELETE FROM cache
        WHERE question = ?
    """, (question,))

    deleted = cursor.rowcount > 0

    connection.commit()
    connection.close()

    return deleted


if __name__ == "__main__":

    create_database()
    print("SmartCache database is ready!")
