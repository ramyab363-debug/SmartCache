# ⚡ SmartCache – Semantic Caching for LLM Applications

SmartCache is a Python-based semantic caching system that identifies similar user queries using text embeddings and vector similarity search. It reuses previously generated responses to avoid unnecessary repeated LLM processing.

## 🚀 Overview

SmartCache combines semantic similarity search with a locally running Large Language Model (LLM).

When a user submits a question, the system checks whether a sufficiently similar question already exists in the cache. If a match is found, the stored response is returned. Otherwise, the query is sent to Gemma through Ollama to generate a new response, which is then stored for future use.

## ✨ Features

- Semantic similarity-based question matching
- Cache HIT and MISS detection
- Configurable similarity threshold (0.80)
- Vector similarity search using FAISS
- Local AI response generation using Gemma 3 1B
- Ollama integration for running the LLM locally
- SQLite database for persistent cache storage
- Cache entry exploration and deletion
- Cache hit rate and processing time monitoring
- Interactive Streamlit dashboard
- Automated unit testing

## 🎬 Demo

Watch SmartCache in action:

[▶ Watch SmartCache Demo](demo/smartcache-demo.mp4.mp4)


The demo demonstrates AI response generation on a cache MISS and response reuse on a semantic cache HIT.

## 🛠️ Technologies Used

- **Python** – Core application logic
- **Streamlit** – Interactive web interface
- **Sentence Transformers** – Text embedding generation
- **FAISS** – Vector similarity search
- **PyTorch** – Embedding-related tensor operations
- **NumPy** – Numerical operations
- **SQLite** – Persistent cache storage
- **Ollama** – Local LLM runtime
- **Gemma 3 1B** – AI response generation

## ⚙️ How It Works

1. A user submits a question through the Streamlit interface.
2. Sentence Transformers converts the question into a numerical embedding.
3. FAISS searches for the most similar cached question.
4. If the similarity score meets the configured threshold, the stored response is returned (**CACHE HIT**).
5. If no suitable match is found, the query is sent to Gemma 3 1B through Ollama (**CACHE MISS**).
6. The generated response and its embedding are stored in SQLite for future retrieval.

## 📁 Project Structure

```text
SmartCache/
│
├── app.py
├── cache.py
├── database.py
├── test_cache.py
├── requirements.txt
├── .gitignore
├── README.md
│
└── demo/
    └── smartcache-demo.mp4
```

## 💻 Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/ramyab363-debug/SmartCache.git
cd SmartCache
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 4. Install and configure Ollama

Download and install Ollama from:

https://ollama.com/download

Pull the Gemma 3 1B model:

```bash
ollama pull gemma3:1b
```

Make sure Ollama is running before starting the application.

### 5. Run SmartCache

```bash
python -m streamlit run app.py
```

Streamlit will provide a local URL to open the application in your browser.

## 🧪 Running Tests

Run the automated test suite using:

```bash
python -m unittest test_cache.py -v
```

The project currently has 13 passing tests.

## 📊 Performance Monitoring

The dashboard displays:

- Cache hits
- Cache misses
- Cache hit rate
- Average processing time
- Number of saved questions

These metrics help observe cache behavior during the current application session.

## 🎓 Learning Outcomes

- Understanding semantic embeddings and similarity search
- Implementing cache HIT/MISS logic
- Integrating a locally running LLM
- Working with FAISS vector indexing
- Managing persistent data using SQLite
- Measuring cache performance and processing time
- Building an interactive application using Streamlit

## 👩‍💻 Author

**Ramya B**

GitHub: https://github.com/ramyab363-debug


---

*SmartCache is a practical project exploring semantic caching and response reuse for LLM applications.*