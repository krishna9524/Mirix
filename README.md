<div align="center">

# 🧠 MIRIX 🤖
### Multi-Agent AI Orchestration & Cognitive Memory System

<p align="center">
  <img src="https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi" />
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/MySQL-4479A1?style=for-the-badge&logo=mysql&logoColor=white" />
  <img src="https://img.shields.io/badge/LangChain-1C3C3C?style=for-the-badge" />
</p>

<p align="center">
  <b>MIRIX</b> is a local-first, highly concurrent AI backend built with FastAPI and LangGraph.  
  It leverages local Large Language Models like <b>Qwen2.5-coder</b> to autonomously execute  
  complex multi-step reasoning tasks across a hybrid cognitive memory architecture.
</p>

</div>

---

# 📑 Table of Contents

- [🚀 System Architecture & Features](#-system-architecture--features)
- [🛠️ Tech Stack](#️-tech-stack)
- [📂 Directory Structure](#-directory-structure)
- [⚙️ Setup & Installation](#️-setup--installation)
- [🔌 API Reference](#-api-reference)
- [🧠 Memory Storage Note](#-memory-storage-note)

---

# 🚀 System Architecture & Features

MIRIX was engineered to explore the frontiers of:

- Multi-Agent Workflows
- Contextual Retrieval
- Cognitive Memory Systems
- Multimodal Processing
- Local LLM Orchestration

---

## 🤖 Multi-Agent Orchestration & Tool Use

Engineered a **ReAct-based agentic workflow** utilizing:

- LangGraph
- LangChain
- Local LLMs via Ollama

Capabilities include:

- Autonomous query routing
- External API invocation
- Internal database querying
- Real-time reasoning streams
- SSE token streaming

### Integrated Tooling

- 🌐 DuckDuckGo Search
- 🧠 Local RAG Retrieval
- 🗂️ Database Access
- 📄 File Retrieval

---

## 🧠 Hybrid Cognitive Memory Framework

Architected a multi-tiered memory system inspired by human cognition.

The system bridges:

- **Relational Storage (MySQL + SQLAlchemy)**
- **Vector Retrieval (FAISS)**

to enable persistent context-aware Retrieval-Augmented Generation (RAG).

### Memory Modules

#### 📌 Episodic Memory
- Stores conversational context
- Maintains long-term session continuity
- Enables contextual RAG retrieval

#### 📁 Resource Memory
- Tracks uploaded resources
- Maps UUIDs to local storage paths
- Links extracted vector chunks

#### 🔮 Planned Modules
- Semantic Memory
- Procedural Memory
- Core Persona Memory

---

## 🖼️ Multimodal Document Intelligence

Built a robust ingestion pipeline for:

- PDF
- DOCX
- TXT
- Images

### OCR & Parsing

Integrated:

- `pytesseract`
- `pdf2image`
- `pypdf`
- `python-docx`

for extracting structured and unstructured data.

### Embedding Architecture

Used dual embedding systems:

| Model | Purpose |
|---|---|
| `all-MiniLM-L6-v2` | Semantic text retrieval |
| `CLIP-ViT-B-32` | Cross-modal image-text retrieval |

---

## ⚡ Scalable Backend Engineering

Developed a highly concurrent backend using FastAPI.

### Key Features

- Async request handling
- Optimized DB session lifecycle
- Pydantic validation models
- Safe client-agent communication
- Modular service architecture

---

# 🛠️ Tech Stack

| Category | Technologies |
|---|---|
| **Framework** | Python 3.10+, FastAPI, Uvicorn |
| **Orchestration & LLMs** | LangChain, LangGraph, Ollama (Qwen2.5-coder:14b) |
| **Relational Database** | MySQL, SQLAlchemy, PyMySQL |
| **Vector Database** | FAISS (`faiss-cpu`) |
| **Embeddings & Vision** | SentenceTransformers, CLIP, Pillow |
| **Document Parsing & OCR** | `pytesseract`, `pdf2image`, `pypdf`, `python-docx`, `python-multipart` |

---

# 📂 Directory Structure

```text
app/
├── api/               # FastAPI routers (chat, memory, files, agents)
├── agents/            # LangGraph orchestrator & specialized agents
├── core/              # Database engine and configuration
├── memory_system/     # Cognitive memory modules
├── models/            # SQLAlchemy models & Pydantic schemas
└── services/          # RAG, Embeddings, FAISS, Multimodal logic
```

---

# ⚙️ Setup & Installation

## 1️⃣ Prerequisites

Ensure the following are installed:

- Python 3.10+
- MySQL Server
- Ollama
- Tesseract OCR

### Install Ollama

Visit:

```bash
https://ollama.ai/
```

---

## 2️⃣ Clone Repository & Install Dependencies

```bash
git clone https://github.com/krishna9524/Mirix.git

cd Mirix

pip install -r requirements.txt
```

---

## 3️⃣ Pull the Local LLM

Ensure Ollama is running locally:

```bash
ollama run qwen2.5-coder:14b
```

---

## 4️⃣ Configure Environment Variables

Create a `.env` file in the project root.

```env
OPENROUTER_API_KEY="your_openrouter_key_here"

# =========================
# MySQL Configuration
# =========================

DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=root
DB_PASS=your_password
DB_NAME=mirix_db
```

---

## 5️⃣ Run the Application

Start the FastAPI development server:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

---

# 🔌 API Reference

---

## `POST /api/v1/chat-stream`

### Description

Send message history and receive:

- Real-time agent reasoning
- Tool invocation logs
- Streamed token responses

### Features

- SSE Streaming
- Multi-Agent Routing
- Live Tool Execution

---

## `POST /api/v1/generate-title`

### Description

Generate a concise 3–5 word title summarizing a conversation.

---

## `POST /api/v1/upload`

### Supported File Types

- PDF
- DOCX
- TXT
- Images

### Processing Pipeline

- OCR extraction
- Text chunking
- Embedding generation
- FAISS indexing

---

## `GET /api/v1/get/{file_id}/{filename}`

Retrieve uploaded files directly from local storage.

---

## `GET /api/v1/agents`

List all available specialized agents registered within MIRIX.

---

# 🧠 Memory Storage Note

---

## 🗄️ SQL Database Storage

Relational metadata stored in MySQL:

```text
memory_chunks
resource_memory
episodic_memory
```

### Purpose

- Persistent chat history
- Session continuity
- Resource tracking
- Metadata management

---

## 🔍 FAISS Vector Storage

Persistent vector indices are saved locally as:

```text
mirix_text_index.faiss
mirix_image_index.faiss
```

### Enables

- Semantic retrieval
- RAG workflows
- Long-context memory
- Cross-modal search

---

> ⚠️ Important:
>
> Do NOT commit `.faiss` index files to version control.

---

<div align="center">

## ⭐ MIRIX — Towards Autonomous Cognitive AI Systems

Built with ❤️ using FastAPI, LangGraph, FAISS, and Local LLMs.

</div>
