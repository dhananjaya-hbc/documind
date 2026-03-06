# 🧠 DocuMind — AI Document Q&A Platform

> Upload any PDF and ask questions about it using AI. Built with RAG (Retrieval-Augmented Generation).

![Python](https://img.shields.io/badge/Python-3.12-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue)
![Docker](https://img.shields.io/badge/Docker-Ready-blue)
![Tests](https://img.shields.io/badge/Tests-23%20Passed-brightgreen)

---

## 🚀 Features

- 📄 **PDF Upload & Processing** — Upload any PDF, text is automatically extracted and chunked
- 🔍 **Semantic Search** — Find relevant content using vector embeddings (not just keyword matching)
- 🤖 **AI-Powered Q&A** — Ask questions and get accurate answers with source citations
- ⚡ **Streaming Responses** — Real-time streaming like ChatGPT
- 🔐 **JWT Authentication** — Secure user registration and login
- 📊 **Conversation History** — All Q&A sessions are saved
- 🐳 **Docker Ready** — One command to run everything


---

## 🔧 Tech Stack

| Technology | Purpose |
|-----------|---------|
| **FastAPI** | Async REST API framework |
| **PostgreSQL** | Relational database (users, documents, chats) |
| **ChromaDB** | Vector database (document embeddings) |
| **SQLAlchemy** | Async ORM for database operations |
| **Sentence-Transformers** | Local text embedding model (free) |
| **OpenRouter** | LLM API gateway (free tier) |
| **JWT (python-jose)** | Token-based authentication |
| **bcrypt** | Password hashing |
| **Alembic** | Database migrations |
| **Docker & Docker Compose** | Containerization |
| **Pydantic** | Data validation |
| **Pytest** | Automated testing |

---

## 📡 API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/register` | Register new user |
| POST | `/api/v1/auth/login` | Login & get JWT token |
| GET | `/api/v1/auth/me` | Get current user profile 🔒 |

### Documents
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/documents/upload` | Upload PDF document 🔒 |
| GET | `/api/v1/documents/` | List all documents 🔒 |
| GET | `/api/v1/documents/{id}` | Get document details 🔒 |
| DELETE | `/api/v1/documents/{id}` | Delete document 🔒 |

### Chat
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/chat/{doc_id}/ask` | Ask question about document 🔒 |
| POST | `/api/v1/chat/{doc_id}/ask/stream` | Ask with streaming response 🔒 |
| GET | `/api/v1/chat/{doc_id}/history` | Get conversation history 🔒 |

🔒 = Requires JWT authentication

---

## 🚀 Quick Start

### Option 1: Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/documind.git
cd documind

# Set up environment variables
cp .env.example .env
# Edit .env and add your OpenRouter API key

# Start everything with one command
docker-compose up -d

# Visit the API docs
open http://localhost:8000/docs

# Clone and setup
git clone https://github.com/YOUR_USERNAME/documind.git
cd documind
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Start PostgreSQL and Redis
docker run -d --name documind-db -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=documind -p 5432:5432 postgres:16-alpine
docker run -d --name documind-redis -p 6379:6379 redis:7-alpine

# Setup environment
cp .env.example .env
# Edit .env with your API key

# Run migrations
alembic upgrade head

# Start the server
uvicorn app.main:app --reload --port 8000

```

## Project Structure

documind/
├── app/
│   ├── main.py              # FastAPI application entry point
│   ├── config.py             # Environment configuration
│   ├── database.py           # PostgreSQL async connection
│   ├── models/               # SQLAlchemy database models
│   │   ├── user.py           # User model
│   │   └── document.py       # Document & Conversation models
│   ├── schemas/              # Pydantic validation schemas
│   │   ├── user.py           # Auth request/response schemas
│   │   └── document.py       # Document & Chat schemas
│   ├── api/                  # API route handlers
│   │   ├── auth.py           # Auth endpoints
│   │   ├── documents.py      # Document endpoints
│   │   └── chat.py           # Chat endpoints
│   ├── services/             # Business logic layer
│   │   ├── auth_service.py   # Authentication logic
│   │   ├── document_service.py # Document processing
│   │   ├── embedding_service.py # Vector embeddings
│   │   ├── llm_service.py    # LLM integration
│   │   └── rag_service.py    # RAG pipeline
│   ├── core/                 # Security & dependencies
│   │   ├── security.py       # JWT & password hashing
│   │   └── dependencies.py   # Auth dependency
│   └── utils/                # Helper utilities
│       ├── pdf_parser.py     # PDF text extraction
│       └── text_chunker.py   # Text chunking with overlap
├── tests/                    # Automated tests
├── alembic/                  # Database migrations
├── docker-compose.yml        # Multi-container setup
├── Dockerfile                # App container definition
└── requirements.txt          # Python dependencies