
import sqlite3
import numpy as np


def create_database():

    connection = sqlite3.connect("smartcache.db")
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cache (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT NOT NULL,
            answer TEXT NOT NULL,
            embedding BLOB NOT NULL
        )
    """)

    connection.commit()
    connection.close()


def save_cache(question, answer, embedding):

    # Convert embedding into a NumPy array
    embedding_array = embedding.cpu().numpy().astype(np.float32)

    # Convert the array into binary data
    embedding_bytes = embedding_array.tobytes()

    connection = sqlite3.connect("smartcache.db")
    cursor = connection.cursor()

    # Check whether the exact question already exists
    cursor.execute("""
        SELECT id FROM cache
        WHERE LOWER(TRIM(question)) = LOWER(TRIM(?))
    """, (question,))

    existing_entry = cursor.fetchone()

    if existing_entry:
        connection.close()
        return False

    # Insert a new cache entry
    cursor.execute("""
        INSERT INTO cache (question, answer, embedding)
        VALUES (?, ?, ?)
    """, (question, answer, embedding_bytes))

    connection.commit()
    connection.close()

    return True


def get_all_cache():

    connection = sqlite3.connect("smartcache.db")
    cursor = connection.cursor()

    cursor.execute("""
        SELECT question, answer, embedding FROM cache
    """)

    rows = cursor.fetchall()
    connection.close()

    cache_entries = []

    for question, answer, embedding_bytes in rows:

        # Convert binary data back into a NumPy array
        embedding_array = np.frombuffer(
            embedding_bytes,
            dtype=np.float32
        ).copy()

        cache_entries.append({
            "question": question,
            "answer": answer,
            "embedding": embedding_array
        })

    return cache_entries


if __name__ == "__main__":
    create_database()
    print("SmartCache database is ready!")
