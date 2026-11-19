
import os
import sqlite3
import tempfile
import unittest

import cache as cache_module
from cache import SemanticCache


class TestSmartCache(unittest.TestCase):

    def setUp(self):

        # Create a separate temporary database for each test
        self.temp_dir = tempfile.TemporaryDirectory()

        self.db_path = os.path.join(
            self.temp_dir.name,
            "test_smartcache.db"
        )

        self.cache = SemanticCache(db_path=self.db_path)

    def tearDown(self):
        self.temp_dir.cleanup()

    def get_database_count(self):

        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()

        cursor.execute("SELECT COUNT(*) FROM cache")

        count = cursor.fetchone()[0]
        connection.close()

        return count

    # TEST 1
    def test_empty_question(self):

        with self.assertRaises(ValueError):
            self.cache.get_answer("")

    # TEST 2
    def test_whitespace_question(self):

        with self.assertRaises(ValueError):
            self.cache.get_answer("     ")

    # TEST 3
    def test_non_string_input(self):

        with self.assertRaises(ValueError):
            self.cache.get_answer(12345)

    # TEST 4
    def test_long_question(self):

        with self.assertRaises(ValueError):
            self.cache.get_answer("A" * 1001)

    # TEST 5
    def test_first_question_is_miss(self):

        result = self.cache.get_answer(
            "What is artificial intelligence?"
        )

        self.assertEqual(result["status"], "MISS")
        self.assertEqual(self.get_database_count(), 1)

    # TEST 6
    def test_duplicate_question_is_hit(self):

        question = "What is machine learning?"

        first = self.cache.get_answer(question)
        second = self.cache.get_answer(question)

        self.assertEqual(first["status"], "MISS")
        self.assertEqual(second["status"], "HIT")
        self.assertEqual(self.get_database_count(), 1)

    # TEST 7
    def test_hit_returns_matched_question(self):

        question = "Explain Python programming."

        self.cache.get_answer(question)

        result = self.cache.get_answer(question)

        self.assertEqual(result["status"], "HIT")
        self.assertEqual(result["matched_question"], question)

    # TEST 8
    def test_miss_returns_closest_question(self):

        original_threshold = cache_module.SIMILARITY_THRESHOLD

        try:
            self.cache.get_answer("Tell me about artificial intelligence.")

            # Force a MISS to test diagnostic information
            cache_module.SIMILARITY_THRESHOLD = 1.1

            result = self.cache.get_answer(
                "Explain database management systems."
            )

            self.assertEqual(result["status"], "MISS")
            self.assertIsNotNone(result["similarity"])
            self.assertIsNotNone(result["matched_question"])

        finally:
            cache_module.SIMILARITY_THRESHOLD = original_threshold

    # TEST 9
    def test_database_persistence(self):

        question = "What is cloud computing?"

        self.cache.get_answer(question)

        # Create a fresh cache using the same database
        new_cache = SemanticCache(db_path=self.db_path)

        result = new_cache.get_answer(question)

        self.assertEqual(result["status"], "HIT")
        self.assertEqual(new_cache.index.ntotal, 1)

    # TEST 10
    def test_faiss_database_synchronization(self):

        self.cache.get_answer("What is Python?")
        self.cache.get_answer("What is SQL?")
        self.cache.get_answer("What is networking?")

        database_count = self.get_database_count()
        faiss_count = self.cache.index.ntotal

        self.assertEqual(database_count, faiss_count)
        self.assertEqual(len(self.cache.cache), faiss_count)


    # TEST 11
    def test_delete_cache_entry(self):
    
            question = "What is artificial intelligence?"
    
            self.cache.get_answer(question)
    
            deleted = self.cache.delete_entry(question)
    
            self.assertTrue(deleted)
            self.assertEqual(self.get_database_count(), 0)
            self.assertEqual(self.cache.index.ntotal, 0)
            self.assertEqual(len(self.cache.cache), 0)
    
        # TEST 12
    def test_delete_nonexistent_entry(self):
    
            deleted = self.cache.delete_entry(
                "This question does not exist."
            )
    
            self.assertFalse(deleted)
    
        # TEST 13
    def test_deletion_persistence(self):
    
            question = "What is cloud computing?"
    
            self.cache.get_answer(question)
    
            self.cache.delete_entry(question)
    
            new_cache = SemanticCache(db_path=self.db_path)
    
            self.assertEqual(new_cache.index.ntotal, 0)
            self.assertEqual(len(new_cache.cache), 0)
            self.assertEqual(self.get_database_count(), 0)
        


if __name__ == "__main__":

    print("\n⚡ SMARTCACHE AUTOMATED TEST SUITE\n")

    unittest.main(verbosity=2)
    
    