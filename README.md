<div align="center">

# 🕵️‍♂️ SceneSolver  
### AI-Powered Crime Video Analysis Platform

<img src="https://img.shields.io/badge/AI-Video%20Analysis-red?style=for-the-badge" />
<img src="https://img.shields.io/badge/Backend-Flask-black?style=for-the-badge" />
<img src="https://img.shields.io/badge/Frontend-React-blue?style=for-the-badge" />
<img src="https://img.shields.io/badge/LLM-Ollama-green?style=for-the-badge" />
<img src="https://img.shields.io/badge/Database-MongoDB-darkgreen?style=for-the-badge" />

<br/>

> 🚨 Analyze crime videos using AI, generate evidence summaries, and chat with a local LLM-powered investigation assistant.

</div>

---

# ✨ Features

✅ AI Crime Classification using CLIP  
✅ Automatic Story Generation with BART  
✅ Video Frame Extraction  
✅ Local LLM Chat Support (Ollama)  
✅ Evidence Labeling System  
✅ Conversational Memory  
✅ Flask REST APIs  
✅ React Frontend Dashboard  
✅ Redis Cache Support  

---

# 🧠 AI Models Used

| Model | Purpose |
|------|------|
| CLIP | Crime Scene Classification |
| BART | Story/Summary Generation |
| Ollama | Local LLM Conversations |

---

# 🛠️ Tech Stack

<div align="center">

| Frontend | Backend | AI/ML | Database |
|---|---|---|---|
| React.js | Flask | CLIP | MongoDB |
| Tailwind CSS | Python | BART | Redis |
| Axios | REST APIs | Ollama | ChromaDB |

</div>

---

# 📂 Project Structure

```bash
SceneSolver/
│
├── backend/
│   ├── app.py
│   ├── routes/
│   ├── services/
│   ├── models/
│   ├── uploads/
│   ├── utils/
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   ├── public/
│   ├── components/
│   └── package.json
│
├── README.md
├── .env
└── .gitignore
```

---

# ⚙️ Setup & Installation

## 1️⃣ Clone Repository

```bash
git clone https://github.com/your-username/scenesolver.git

cd scenesolver
```

---

## 2️⃣ Backend Setup

```bash
cd backend

pip install -r requirements.txt
```

---

## 3️⃣ Frontend Setup

```bash
cd ../frontend

npm install
```

---

# 🧠 Pull the Local LLM

SceneSolver uses **Ollama** for running local AI models.

---

## 📥 Install Ollama

```bash
https://ollama.com/download
```

---

## 🚀 Pull Llama 3

```bash
ollama pull llama3
```

---

## 🔥 Alternative Models

```bash
ollama pull mistral

ollama pull gemma
```

---

## ✅ Verify Ollama

```bash
ollama run llama3
```

---

# 🔐 Environment Variables

Create a `.env` file inside the `backend/` folder.

```env
# MongoDB
MONGO_URI=your_mongodb_connection

# Flask
SECRET_KEY=your_secret_key

# Ollama
OLLAMA_MODEL=llama3
OLLAMA_BASE_URL=http://localhost:11434

# Redis
REDIS_URL=your_redis_url

# Uploads
UPLOAD_FOLDER=uploads
```

---

# ▶️ Run the Application

## 🚀 Start Backend

```bash
cd backend

python app.py
```

### Backend URL

```bash
http://localhost:5000
```

---

## 💻 Start Frontend

```bash
cd frontend

npm start
```

### Frontend URL

```bash
http://localhost:3000
```

---

# 🔌 API Reference

# 📤 Upload Video

### Endpoint

```http
POST /api/upload
```

### Request

```bash
FormData:
video=<video_file>
```

### Response

```json
{
  "message": "Video uploaded successfully",
  "video_id": "12345"
}
```

---

# 🧠 Analyze Video

### Endpoint

```http
POST /api/analyze/<video_id>
```

### Response

```json
{
  "crime_type": "Robbery",
  "summary": "Masked suspect entered through back door..."
}
```

---

# 💬 Chat with AI

### Endpoint

```http
POST /api/chat
```

### Request

```json
{
  "message": "Explain the crime scene"
}
```

### Response

```json
{
  "response": "The suspect entered the building at 2:14 AM..."
}
```

---

# 🧠 Memory Storage Note

SceneSolver supports contextual AI conversations using memory-aware architecture.

---

## 🗂️ Current Memory System

- Temporary conversation storage
- Prompt history tracking
- Cached video analysis results
- Redis-based fast retrieval

---

## 🏗️ Recommended Production Architecture

| Component | Purpose |
|---|---|
| Redis | Short-term AI memory |
| MongoDB | Persistent chat storage |
| ChromaDB | Vector embeddings |
| FAISS | Semantic similarity search |

---

# 📸 Screenshots

<div align="center">

| Dashboard | AI Analysis | Chat Assistant |
|---|---|---|
| Add screenshots here | Add screenshots here | Add screenshots here |

</div>

---

# 📈 Future Improvements

- 🎥 Real-time CCTV Monitoring  
- 👤 Face Recognition  
- 🎙️ Voice Transcription  
- 🧠 RAG-based Investigation Assistant  
- 📍 Timeline Reconstruction  
- 🚓 Multi-Camera Tracking  
- ☁️ Cloud Deployment Support  

---

# 🤝 Contributing

```bash
# Fork Repository

# Create Feature Branch
git checkout -b feature-name

# Commit Changes
git commit -m "Added new feature"

# Push Branch
git push origin feature-name
```

Then create a Pull Request 🚀

---

# 📜 License

Licensed under the **MIT License**

---

# ⭐ Support

If you like this project:

🌟 Star the repository  
🍴 Fork the project  
🛠️ Contribute improvements  
📢 Share with others  

---

<div align="center">

# 🚨 SceneSolver
### Smart AI For Smarter Investigations

Made with ❤️ using Flask, React & AI

</div>
