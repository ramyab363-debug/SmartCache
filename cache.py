
from sentence_transformers import SentenceTransformer
import torch
import numpy as np
import faiss
import time

from database import create_database, save_cache, get_all_cache


# Load the embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

SIMILARITY_THRESHOLD = 0.80
EMBEDDING_DIMENSION = 384


class SemanticCache:

    def __init__(self):

        create_database()

        # Create FAISS index
        self.index = faiss.IndexFlatIP(EMBEDDING_DIMENSION)

        # Load saved entries from SQLite
        saved_entries = get_all_cache()

        self.cache = []
        self.hit_count = 0
        self.miss_count = 0
        self.total_latency = 0.0

        for item in saved_entries:

            embedding = np.asarray(
                item["embedding"],
                dtype=np.float32
            ).reshape(1, -1)

            # Normalize for cosine similarity
            faiss.normalize_L2(embedding)

            # Add embedding to FAISS
            self.index.add(embedding)

            self.cache.append({
                "question": item["question"],
                "answer": item["answer"],
                "embedding": embedding.copy()
            })

    def generate_answer(self, question):

        # Temporary simulated AI response
        return f"Demo AI response for: {question}"

    def get_answer(self, question):

                # Validate the question
        if not isinstance(question, str):
            raise ValueError("Question must be text.")

        question = question.strip()

        if not question:
            raise ValueError("Question cannot be empty.")

        if len(question) > 1000:
            raise ValueError("Question cannot exceed 1000 characters.")

        # Start measuring processing time
        start_time = time.perf_counter()

        # Generate embedding for new question
        question_embedding = model.encode(
            question,
            convert_to_numpy=True
        ).astype(np.float32)

        question_embedding = question_embedding.reshape(1, -1)

        # Normalize the query embedding
        faiss.normalize_L2(question_embedding)

        # Search for the closest cached question
        if self.index.ntotal > 0:

            scores, indices = self.index.search(
                question_embedding,
                1
            )

            similarity = float(scores[0][0])
            matched_index = int(indices[0][0])

            if similarity >= SIMILARITY_THRESHOLD:

                matched_item = self.cache[matched_index]

                # Update HIT count
                self.hit_count += 1

                # Calculate latency
                latency = time.perf_counter() - start_time
                self.total_latency += latency

                return {
                    "answer": matched_item["answer"],
                    "status": "HIT",
                    "similarity": similarity,
                    "matched_question": matched_item["question"],
                    "latency": latency
                }

        # No sufficiently similar question found
        answer = self.generate_answer(question)

        # Save embedding to SQLite
       
        # Save embedding to SQLite
        embedding_tensor = torch.from_numpy(
            question_embedding.flatten().copy()
        )

        saved = save_cache(
            question,
            answer,
            embedding_tensor
        )

        # Update FAISS only if SQLite saved a new entry
        if saved:

            self.index.add(question_embedding)

            self.cache.append({
                "question": question,
                "answer": answer,
                "embedding": question_embedding.copy()
            })


        # Update MISS count
        self.miss_count += 1

        # Calculate latency
        latency = time.perf_counter() - start_time
        self.total_latency += latency

        return {
            "answer": answer,
            "status": "MISS",
            "similarity": None,
            "latency": latency
        }
