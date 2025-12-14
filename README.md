# 🧠 RAG-Based Chatbot for Any Website URL

A  headless Retrieval-Augmented Generation (RAG) backend** that crawls any website, builds a per-site knowledge base, and answers user questions using semantic search + LLMs.

This project is designed to be:
- ✅ Multi-user
- ✅ Deployable
- ✅ Frontend-agnostic (React, Streamlit, mobile, etc.)
- ✅ Scalable & modular

---

## 🚀 Features

- 🌐 Crawl any public website (up to configurable depth)
- 🧹 Clean & preprocess HTML content
- ✂️ Chunk text intelligently
- 🧠 Generate embeddings using Sentence Transformers
- 📦 Store vectors using FAISS (per-website isolation)
- 🔎 Retrieve relevant context via semantic search
- 🤖 Generate answers using **Groq LLMs**
- 🧩 Headless REST APIs (FastAPI)

---

## 🏗️ High-Level Architecture

```
┌──────────────┐
│   Frontend   │  (React / Streamlit / Any Client)
└──────┬───────┘
       │ HTTPS (JSON)
       ▼
┌──────────────────────────┐
│     FastAPI Backend      │
│  (Stateless, Headless)   │
└─────────┬────────────────┘
          │
          │
 ┌────────▼────────┐
 │  Crawl Service   │
 │  (Website → KB)  │
 └────────┬────────┘
          │
          ▼
 ┌──────────────────────┐
 │ Knowledge Base (KB)  │
 │  - Clean text        │
 │  - Chunking          │
 │  - Embeddings        │
 │  - FAISS Index       │
 └────────┬─────────────┘
          │
          ▼
 ┌──────────────────────┐
 │   RAG Chat Service   │
 │  - Semantic Search  │
 │  - Prompt Builder   │
 │  - Groq LLM         │
 └──────────────────────┘
```

---

## 🧩 Detailed Component Architecture

```
rag-backend/
│
├── api/
│   ├── main.py              # FastAPI app entry
│   └── routes/
│       ├── crawl.py         # /api/crawl
│       └── chat.py          # /api/chat
│
├── services/
│   ├── crawl_service.py     # Crawl + KB workflow
│   └── chat_service.py      # RAG query workflow
│
├── core/
│   ├── crawler/
│   │   ├── crawler.py       # Website crawling logic
│   │   └── utils.py
│   │
│   ├── kb/
│   │   ├── build_kb.py      # Chunking + embedding
│   │   └── vector_store.py  # FAISS save/load
│   │
│   └── rag/
│       └── qa_chain.py      # Retrieval + LLM logic
│
├── schemas/
│   ├── crawl.py             # Request/response models
│   └── chat.py
│
├── utils/
│   └── url_hash.py          # URL → kb_id
│
├── storage/
│   └── data/
│       └── <kb_id>/         # One folder per website
│           ├── raw_pages.json
│           ├── faiss.index
│           └── metadata.pkl
│
├── .env                     # Environment variables
├── requirements.txt
└── README.md
```

---

## 🔄 End-to-End Data Flow

### 1️⃣ Build Knowledge Base

```
Client → POST /api/crawl
        ↓
Backend:
- Validate URL
- Generate kb_id
- Crawl website
- Clean & extract text
- Chunk content
- Generate embeddings
- Store FAISS index
```

### 2️⃣ Ask a Question

```
Client → POST /api/chat
        ↓
Backend:
- Load FAISS index by kb_id
- Embed user question
- Retrieve top-k chunks
- Build RAG prompt
- Query Groq LLM
- Return answer + sources
```

---

## 🌐 API Reference

### 🔹 Health Check
```
GET /health
```
Response:
```json
{ "status": "ok" }
```

---

### 🔹 Crawl Website
```
POST /api/crawl
```
Request:
```json
{
  "url": "https://example.com"
}
```
Response:
```json
{
  "kb_id": "example_com",
  "status": "completed",
  "pages_crawled": 1
}
```

---

### 🔹 Chat with Website
```
POST /api/chat
```
Request:
```json
{
  "kb_id": "example_com",
  "question": "What is this website about?"
}
```
Response:
```json
{
  "answer": "Example.com is used for illustrative purposes.",
  "sources": ["https://example.com"]
}
```

---

## 🔐 Environment Variables

Create a `.env` file:

```env
GROQ_API_KEY=your_groq_api_key_here
```

---

## 🧠 Design Decisions & Rationale

- **Stateless backend** → scalable & cloud-friendly
- **Per-website vector stores** → multi-user safe
- **FAISS** → fast local vector search
- **Sentence Transformers** → high-quality embeddings
- **Groq LLMs** → fast inference & free tier
- **FastAPI** → async, high performance, OpenAPI support

---

## 🚀 Deployment Ready

This backend is ready for:
- Dockerization
- Render / Railway / AWS / Azure
- Integration with React or any frontend

---

## 🏆 What This Project Demonstrates

- Real-world RAG architecture
- Backend system design
- API-first development
- LLM integration
- Vector databases
- Clean, modular codebase

---

## 📌 Future Enhancements

- Authentication & rate limiting
- Chat history & sessions
- Streaming responses
- Hybrid search (BM25 + vectors)
- UI dashboard (React)

---

## 🐳 Docker Deployment

1.  **Environment Variables**: Ensure your `.env` file exists and contains `GROQ_API_KEY`. The `docker-compose.yml` is configured to read this file automatically.

2.  **Build and Run**:
    ```bash
    docker-compose up --build -d
    ```

3.  **Persistence**: The `storage/` directory is mounted to the container. Data crawled inside Docker will appear in your local `storage` folder and persist across restarts.

4.  **Access**: The API will be available at `http://localhost:8000`.

---
