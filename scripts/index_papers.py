import os
import sys
import json
import sqlite3
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from config import Config

MAX_FEATURES = 500


def process_and_index_sections():
    conn = sqlite3.connect(Config.DB_PATH)
    cursor = conn.cursor()

    try:
        # Ensure column exists
        cursor.execute("PRAGMA table_info(paper_sections);")
        columns = [column[1] for column in cursor.fetchall()]
        if "tfidf_vector" not in columns:
            cursor.execute("ALTER TABLE paper_sections ADD COLUMN tfidf_vector TEXT;")

        # Fetch sections
        cursor.execute("SELECT id, text FROM paper_sections WHERE text IS NOT NULL AND text != '';")
        rows = cursor.fetchall()

        if not rows:
            print("No paper sections found to index.")
            return

        section_ids, texts = zip(*rows)

        # Fit TF-IDF
        vectorizer = TfidfVectorizer(max_features=MAX_FEATURES, stop_words="english")
        tfidf_matrix = vectorizer.fit_transform(texts).toarray()

        # Save model
        os.makedirs(os.path.dirname(Config.VECTORIZER_PATH), exist_ok=True)
        joblib.dump(vectorizer, Config.VECTORIZER_PATH)

        # Update DB using JSON stringified lists
        update_data = [
            (json.dumps(vector.tolist()), sec_id)
            for sec_id, vector in zip(section_ids, tfidf_matrix)
        ]

        cursor.executemany(
            "UPDATE paper_sections SET tfidf_vector = ? WHERE id = ?;",
            update_data
        )
        conn.commit()
        print(f"Successfully indexed {len(update_data)} paper sections into SQLite.")

    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    process_and_index_sections()