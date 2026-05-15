from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import chat, memory, agents, files
from app.core.database import engine, Base
import app.models.db_models  # <--- ADD THIS LINE TO IMPORT YOUR MODELS

# This creates all your tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="MIRIX Backend")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],
)

# Include your API routers
app.include_router(chat.router, prefix="/api/v1", tags=["Chat"])
app.include_router(memory.router, prefix="/api/v1", tags=["Memory"])
app.include_router(agents.router, prefix="/api/v1", tags=["Agents"])
app.include_router(files.router, prefix="/api/v1", tags=["Files"])  # <-- ADD THIS LINE

@app.get("/")
def read_root():
    return {"message": "Welcome to the MIRIX API"}