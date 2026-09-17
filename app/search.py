import json
import joblib
import sqlite3
import numpy as np
from flask import current_app
from sklearn.metrics.pairwise import cosine_similarity

class PaperSearcher:
    def __init__(self, vectorizer_path):
        self.vectorizer = joblib.load(vectorizer_path)

    def search(self, query_text: str, top_k: int = 5, threshold: float = 0.1):
        if not query_text.strip():
            return []

        query_vector = self.vectorizer.transform([query_text]).toarray()

        conn = sqlite3.connect(current_app.config["DB_PATH"])
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT p.id, p.title, p.url, ps.section_number, ps.tfidf_vector
                FROM paper_sections ps
                JOIN papers p ON p.id = ps.paper_id
                WHERE ps.tfidf_vector IS NOT NULL;
            """)
            rows = cursor.fetchall()
            if not rows:
                return []

            paper_ids, titles, urls, section_numbers, vector_strings = zip(*rows)

            # Convert JSON string arrays back to 2D numpy array
            db_matrix = np.array([json.loads(v) for v in vector_strings])

            similarities = cosine_similarity(query_vector, db_matrix)[0]

            results = []
            for idx, score in enumerate(similarities):
                if score >= threshold:
                    results.append({
                        "paper_id": paper_ids[idx],
                        "title": titles[idx],
                        "url": urls[idx],
                        "section_number": section_numbers[idx],
                        "score": round(float(score), 4)
                    })

            results.sort(key=lambda x: x["score"], reverse=True)

            seen_papers = set()
            top_papers = []
            for item in results:
                if item["paper_id"] not in seen_papers:
                    seen_papers.add(item["paper_id"])
                    top_papers.append(item)
                if len(top_papers) == top_k:
                    break

            return top_papers

        finally:
            cursor.close()
            conn.close()