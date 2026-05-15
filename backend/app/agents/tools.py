from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool
from app.services.vector_db_service import vector_db_service
from app.models.db_models import MemoryChunk
from app.core.database import SessionLocal
from sqlalchemy.orm import Session
from typing import Type

# --- Tool for 🧠 Episodic Memory (Text RAG) ---
class EpisodicSearchInput(BaseModel):
    query: str = Field(description="The text query to search for in past conversations.")

class EpisodicMemoryTool(BaseTool):
    name: str = "search_past_conversations"
    description: str = "Searches for relevant text snippets from past conversations."
    args_schema: Type[BaseModel] = EpisodicSearchInput
    db: Session

    def _run(self, query: str) -> str:
        # ... (this tool is unchanged and works)
        print(f"--- Using EpisodicMemoryTool with query: {query} ---")
        try:
            chunk_ids = vector_db_service.search_similar_text(query, k=3)
            if not chunk_ids:
                return "No relevant past conversations found."
            
            relevant_chunks = self.db.query(MemoryChunk.content).filter(
                MemoryChunk.id.in_(chunk_ids),
                MemoryChunk.memory_type == "episodic"
            ).all()
            
            context = "\n---\n".join([chunk.content for chunk in relevant_chunks])
            return f"Found relevant context:\n{context}"
        except Exception as e:
            return f"Error searching memory: {e}"

# --- Tool for 🧩 Image Memory (SigLIP/CLIP) ---
class ImageSearchInput(BaseModel):
    query: str = Field(description="A text query to find a relevant image from the past (e.g., 'that screenshot of the code error').")

class ImageSearchTool(BaseTool):
    name: str = "search_past_images"
    description: str = "Searches for relevant images from the user's past uploads based on a text description."
    args_schema: Type[BaseModel] = ImageSearchInput
    db: Session

    def _run(self, query: str) -> str:
        """Use the tool."""
        print(f"--- Using ImageSearchTool with query: {query} ---")
        try:
            # This searches the *image* vector index
            chunk_ids = vector_db_service.search_similar_images(query, k=1)
            if not chunk_ids:
                return "No relevant images found matching that description."

            # Get the file path/name from the SQL chunk
            chunk = self.db.query(MemoryChunk.content).filter(MemoryChunk.id == chunk_ids[0]).first()
            if not chunk:
                return "Image record not found in SQL."
                
            # Returns the *description* of the file, not the image itself
            return f"Found a relevant image: {chunk.content}. The main model can be used to analyze it if it was just uploaded."
        except Exception as e:
            return f"Error searching images: {e}"