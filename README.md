# SmartCache – Semantic Cache for LLM Applications

A Python-based semantic caching system designed to reduce repeated processing of similar user queries by identifying semantically related questions and reusing previously stored responses.

## Overview

SmartCache uses similarity-based matching to determine whether an incoming question is sufficiently similar to a previously stored question.

Instead of processing every repeated or similar query again, the system can retrieve a cached response when the similarity score meets a configurable threshold.

## Features

- Semantic similarity-based question matching
- Cache HIT and MISS detection
- Configurable similarity threshold
- Response reuse for matching queries
- SQLite database integration for persistence
- Cache hit tracking and latency measurement
- Python-based implementation

## Project Structure

```text
SmartCache/
│
├── app.py
├── cache.py
├── database.py
├── test_embeddings.py
├── requirements.txt
├── .gitignore
└── README.md
```

## Technologies Used

- Python
- Semantic embeddings
- Similarity matching
- SQLite
- NumPy
- OpenCV / other dependencies only if listed in requirements

## How It Works

1. A user submits a question.
2. The system compares it with previously cached questions using semantic similarity.
3. If the similarity score meets the configured threshold, the cached response is returned (**CACHE HIT**).
4. Otherwise, the query follows the cache-miss processing path (**CACHE MISS**).
5. Cache information and responses can be stored using SQLite.

## Installation

Clone the repository:

```bash
git clone https://github.com/ramyab363-debug/SmartCache.git
```

Navigate to the project:

```bash
cd SmartCache
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Run the Application

```bash
python app.py
```

## Learning Outcomes

- Understanding semantic similarity and embeddings
- Implementing cache HIT/MISS logic
- Working with SQLite database persistence
- Measuring cache performance and latency
- Organizing a Python application into modular components

## Author

**Ramya B**

GitHub: https://github.com/ramyab363-debug

---

*This project is being developed as a practical exploration of semantic caching for LLM applications.*