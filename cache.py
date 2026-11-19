
from sentence_transformers import SentenceTransformer
import torch
import numpy as np
import faiss
import time
import json
import urllib.request
import urllib.error

from database import (
    create_database,
    save_cache,
    get_all_cache,
    delete_cache
)


# Load the embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

SIMILARITY_THRESHOLD = 0.80
EMBEDDING_DIMENSION = 384


class SemanticCache:

    def __init__(self, db_path="smartcache.db"):

        self.db_path = db_path

        create_database(self.db_path)

        # Create FAISS index
        self.index = faiss.IndexFlatIP(EMBEDDING_DIMENSION)

        # Load saved entries from SQLite
        saved_entries = get_all_cache(self.db_path)

        self.cache = []
        self.hit_count = 0
        self.miss_count = 0
        self.total_latency = 0.0

        for item in saved_entries:

            embedding = np.asarray(
                item["embedding"],
                dtype=np.float32
            ).reshape(1, -1)

            if embedding.shape[1] != EMBEDDING_DIMENSION:
                raise ValueError("Invalid embedding dimension.")

            faiss.normalize_L2(embedding)

            self.index.add(embedding)

            self.cache.append({
                "question": item["question"],
                "answer": item["answer"],
                "embedding": embedding.copy(),
                "created_at": item["created_at"]
            })

    def generate_answer(self, question):

        # Connect to Ollama's local API
        url = "http://localhost:11434/api/generate"

        payload = {
            "model": "gemma3:1b",
            "prompt": question,
            "stream": False
        }

        data = json.dumps(payload).encode("utf-8")

        request = urllib.request.Request(
            url,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST"
        )

        try:
            with urllib.request.urlopen(
                request,
                timeout=120
            ) as response:

                result = json.loads(
                    response.read().decode("utf-8")
                )

            return result["response"].strip()

        except urllib.error.URLError as error:
            raise RuntimeError(
                "Could not connect to Ollama. "
                "Please make sure Ollama is running."
            ) from error

        except (KeyError, json.JSONDecodeError) as error:
            raise RuntimeError(
                "Could not read the response from Gemma."
            ) from error

    def get_answer(self, question):

        # Validate question
        if not isinstance(question, str):
            raise ValueError("Question must be text.")

        question = question.strip()

        if not question:
            raise ValueError("Question cannot be empty.")

        if len(question) > 1000:
            raise ValueError("Question cannot exceed 1000 characters.")

        start_time = time.perf_counter()

        # Generate embedding
        question_embedding = model.encode(
            question,
            convert_to_numpy=True
        ).astype(np.float32)

        question_embedding = question_embedding.reshape(1, -1)

        if question_embedding.shape[1] != EMBEDDING_DIMENSION:
            raise ValueError("Invalid embedding dimension.")

        faiss.normalize_L2(question_embedding)

        # Search for closest cached question
        best_similarity = None
        best_match_question = None

        if self.index.ntotal > 0:

            scores, indices = self.index.search(
                question_embedding,
                1
            )

            similarity = float(scores[0][0])
            matched_index = int(indices[0][0])

            best_similarity = similarity
            best_match_question = self.cache[matched_index]["question"]

            if similarity >= SIMILARITY_THRESHOLD:

                matched_item = self.cache[matched_index]

                self.hit_count += 1

                latency = time.perf_counter() - start_time
                self.total_latency += latency

                return {
                    "answer": matched_item["answer"],
                    "status": "HIT",
                    "similarity": similarity,
                    "matched_question": matched_item["question"],
                    "latency": latency
                }

        # Generate a real AI answer using Gemma through Ollama
        answer = self.generate_answer(question)

        embedding_tensor = torch.from_numpy(
            question_embedding.flatten().copy()
        )

        saved = save_cache(
            question,
            answer,
            embedding_tensor,
            self.db_path
        )

        # Update FAISS only if SQLite saved a new entry
        if saved:

            # Retrieve saved timestamp from SQLite
            saved_entries = get_all_cache(self.db_path)

            saved_item = next(
                item for item in saved_entries
                if item["question"] == question
            )

            # Update FAISS index
            self.index.add(question_embedding)

            # Update in-memory cache
            self.cache.append({
                "question": question,
                "answer": answer,
                "embedding": question_embedding.copy(),
                "created_at": saved_item["created_at"]
            })

        self.miss_count += 1

        latency = time.perf_counter() - start_time
        self.total_latency += latency

        return {
            "answer": answer,
            "status": "MISS",
            "similarity": best_similarity,
            "matched_question": best_match_question,
            "latency": latency
        }

    def delete_entry(self, question):

        # Delete the entry from SQLite
        deleted = delete_cache(question, self.db_path)

        if deleted:

            # Reload saved entries from SQLite
            saved_entries = get_all_cache(self.db_path)

            # Create a fresh FAISS index
            self.index = faiss.IndexFlatIP(
                EMBEDDING_DIMENSION
            )

            self.cache = []

            # Rebuild FAISS index from saved entries
            for item in saved_entries:

                embedding = np.asarray(
                    item["embedding"],
                    dtype=np.float32
                ).reshape(1, -1)

                if embedding.shape[1] != EMBEDDING_DIMENSION:
                    raise ValueError("Invalid embedding dimension.")

                faiss.normalize_L2(embedding)

                self.index.add(embedding)

                self.cache.append({
                    "question": item["question"],
                    "answer": item["answer"],
                    "embedding": embedding.copy(),
                    "created_at": item["created_at"]
                })

        return deleted
