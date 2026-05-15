<<<<<<< HEAD

---

```markdown
# MIRIX 🧠🤖 
**Multi-Agent AI Orchestration & Cognitive Memory System**

MIRIX is a local-first, highly concurrent AI backend built with FastAPI and LangGraph. It leverages local Large Language Models (like Qwen2.5-coder) to execute complex, multi-step reasoning tasks across a custom hybrid cognitive memory architecture. 

## 🚀 Key Features

* **ReAct Multi-Agent Orchestration:** Utilizes LangGraph to create autonomous agents capable of routing queries, invoking tools (e.g., DuckDuckGo for live web search), and querying internal vector databases.
* **Real-Time Streaming:** Implements Server-Sent Events (SSE) to stream AI thought processes, tool executions, and token generation back to the client in real-time.
* **Hybrid Cognitive Memory System:**
    * **Episodic Memory:** RAG-enabled chat history storing session context in both relational databases and vector indices.
    * **Resource Memory:** Persistent tracking of uploaded files, linking UUIDs and disk paths to extracted vector chunks.
    * *(Planned)* Semantic, Procedural, and Core memory modules for personas and factual grounding.
* **Multimodal Document Intelligence:** Robust ingestion pipeline for PDFs, DOCX, TXT, and Images. Includes OCR capabilities using Tesseract to extract text from scanned documents and images.
* **Dual Vector Embeddings:** Uses `SentenceTransformers` to generate embeddings. Employs `all-MiniLM-L6-v2` for standard text and `clip-ViT-B-32` for cross-modal image-to-text retrieval.

## 🛠️ Tech Stack

* **Framework:** FastAPI, Uvicorn
* **Orchestration & LLMs:** LangChain, LangGraph, Ollama (Qwen2.5-coder:14b)
* **Database (Relational):** MySQL, SQLAlchemy, PyMySQL
* **Database (Vector):** FAISS (`faiss-cpu`)
* **Embeddings & Vision:** SentenceTransformers, CLIP, Pillow
* **Document Parsing & OCR:** `pytesseract`, `pdf2image`, `pypdf`, `python-docx`, `python-multipart`

## 📂 Architecture Overview

```text
app/
├── api/          # FastAPI routers (chat, memory, files, agents)
├── agents/       # LangGraph Orchestrator and specialized sub-agents
├── core/         # Database engine and config settings
├── memory_system/# Cognitive memory modules (Episodic, Resource, Semantic)
├── models/       # SQLAlchemy DB models & Pydantic schemas
└── services/     # RAG, Embeddings, FAISS, and future Multimodal logic

```

## ⚙️ Setup & Installation

### 1. Prerequisites

* Python 3.10+
* MySQL Server running locally or remotely.
* [Ollama](https://ollama.ai/) installed and running locally.
* Tesseract OCR installed on your system (required for image/PDF parsing).

### 2. Install Dependencies

Clone the repository and install the required Python packages:

```bash
pip install -r requirements.txt

```

### 3. Pull the Local LLM

Ensure Ollama is running, then pull the default model:

```bash
ollama run qwen2.5-coder:14b

```

### 4. Environment Variables

Create a `.env` file in the root directory and configure your database and API keys:

```env
OPENROUTER_API_KEY="your_openrouter_key_here"

# MySQL Config
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=root
DB_PASS=your_password
DB_NAME=mirix_db

```

### 5. Run the Application

Start the FastAPI server using Uvicorn:

```bash
uvicorn main:app --host 0.0.0.1 --port 8000 --reload

```

## 🔌 API Endpoints

* `POST /api/v1/chat-stream`: Send message history and receive an SSE stream of the agent's response and tool usage.
* `POST /api/v1/generate-title`: Generate a 3-5 word summary title for a chat session.
* `POST /api/v1/upload`: Upload files (PDF, DOCX, TXT, Images). Automatically extracts text via OCR and adds it to the FAISS vector database.
* `GET /api/v1/get/{file_id}/{filename}`: Retrieve an uploaded file directly from local storage.
* `GET /api/v1/agents`: List all available specialized agents.

## 🧠 Memory Components

* **SQL Database:** Stores relational metadata (`memory_chunks`, `resource_memory`, `episodic_memory`).
* **FAISS Indices:** Saves flat L2 indices locally as `mirix_text_index.faiss` and `mirix_image_index.faiss` for persistent vector retrieval across restarts.

```

```
=======
# Mirix
>>>>>>> 10c093b1de1a0a208ac553b0149f3e37c3b88386
