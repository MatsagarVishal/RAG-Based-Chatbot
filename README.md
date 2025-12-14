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

## 🚀 Deployment

This backend supports multiple deployment options:

### 🏠 Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium

# Create .env file
cp .env.example .env
# Edit .env and add your GROQ_API_KEY

# Run locally
uvicorn api.main:app --reload
```

### 🐳 Docker (Local)

```bash
# Create .env file
cp .env.example .env
# Edit .env with your configuration

# Build and run
docker-compose up --build -d

# View logs
docker-compose logs -f

# Access API
curl http://localhost:8000/health
```

### ☁️ AWS EC2 Deployment (Recommended)

**Quick Start:**

1. **Create S3 Bucket** (for persistent storage):
   ```bash
   aws s3 mb s3://rag-chatbot-storage-<your-unique-id>
   ```

2. **Launch EC2 Instance** (t3.medium or larger recommended)

3. **SSH into EC2 and run setup script**:
   ```bash
   curl -O https://raw.githubusercontent.com/your-repo/rag-chatbot/main/ec2-setup.sh
   chmod +x ec2-setup.sh
   ./ec2-setup.sh
   ```

4. **Configure environment** (`.env`):
   ```env
   GROQ_API_KEY=your_key_here
   STORAGE_BACKEND=s3
   S3_BUCKET_NAME=rag-chatbot-storage-<your-unique-id>
   AWS_REGION=us-east-1
   ```

5. **Access your API**:
   ```
   http://<EC2_PUBLIC_IP>:8000
   ```

📚 **[Complete EC2 Deployment Guide](./docs/ec2-deployment.md)** - Detailed step-by-step instructions

### 🌐 Other Cloud Platforms

- **AWS App Runner**: Fully managed, auto-scaling (~$26-50/month)
- **AWS ECS Fargate**: Production-grade containers (~$80-120/month)
- **Render**: Easy deployment with free tier
- **Railway**: Simple deployment with automatic HTTPS

---

## ⚙️ Configuration

### Environment Variables

Create a `.env` file (use `.env.example` as template):

```env
# Required
GROQ_API_KEY=your_groq_api_key_here

# Storage Backend ('local' or 's3')
STORAGE_BACKEND=local

# Local Storage (only if STORAGE_BACKEND=local)
STORAGE_ROOT=storage/data

# AWS S3 Storage (only if STORAGE_BACKEND=s3)
S3_BUCKET_NAME=rag-chatbot-storage
AWS_REGION=us-east-1

# Optional
PORT=8000
LOG_LEVEL=INFO
```

### Storage Backends

**Local Storage** (Development):
- Data stored in `storage/data/` directory
- Fast, no external dependencies
- Data lost if container is removed

**S3 Storage** (Production):
- Data persisted in AWS S3
- Survives container restarts
- Enables horizontal scaling
- Automatic backups with versioning

---

## 🏆 What This Project Demonstrates

- Real-world RAG architecture
- Backend system design
- API-first development
- LLM integration
- Vector databases (FAISS)
- Cloud-native deployment (AWS S3 integration)
- Docker containerization
- Clean, modular codebase

---

## 📌 Future Enhancements

- Authentication & rate limiting
- Chat history & sessions
- Streaming responses
- Hybrid search (BM25 + vectors)
- UI dashboard (React)
- Migration to managed vector DB (Pinecone, Weaviate)

---

