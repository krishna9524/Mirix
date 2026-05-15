from .base_memory import BaseMemory
from sqlalchemy.orm import Session
from app.models.db_models import MemoryChunk, EpisodicMemory as EpisodicMemoryModel
from app.services.embedding_service import embedding_service
from app.services.vector_db_service import vector_db_service

class EpisodicMemory(BaseMemory):

    def __init__(self, db_session: Session):
        super().__init__(db_session)
        print("Initializing Episodic Memory (RAG-enabled)...")

    # --- THIS IS THE METHOD YOUR ORCHESTRATOR IS LOOKING FOR ---
    def add_chat_message(self, session_id: str, text: str):
        """
        Adds a user's chat message to the episodic memory.
        1. Saves to SQL.
        2. Creates embedding.
        3. Saves to Vector DB (FAISS).
        """
        if not text:
            return

        try:
            # Find or create the session
            session = self.db.query(EpisodicMemoryModel).filter_by(session_id=session_id).first()
            if not session:
                session = EpisodicMemoryModel(session_id=session_id)
                self.db.add(session)
                self.db.commit()

            # 1. Save to SQL database
            new_chunk = MemoryChunk(
                memory_type="episodic",
                content=text,
                episodic_memory_id=session.id
            )
            self.db.add(new_chunk)
            self.db.commit()
            self.db.refresh(new_chunk) # Get the new_chunk.id

            # 2. Create embedding
            embedding = embedding_service.create_text_embedding(text)

            # 3. Save to Vector DB
            if embedding:
                vector_db_service.add_text_embedding(embedding, new_chunk.id)
            
            # 4. Save the vector index to disk (for persistence)
            vector_db_service.save_indices()
            
            print(f"EpisodicMemory: Added chunk {new_chunk.id} for session {session_id}.")

        except Exception as e:
            self.db.rollback()
            print(f"Error in add_chat_message: {e}")

    def retrieve_relevant_chats(self, query_text: str, k: int = 3) -> list[str]:
        """
        Finds the most relevant past chat messages from the vector database.
        """
        try:
            # 1. Search FAISS for the most similar chunk IDs
            chunk_ids = vector_db_service.search_similar_text(query_text, k)
            
            if not chunk_ids:
                return []

            # 2. Retrieve the text for those chunks from the SQL database
            relevant_chunks = self.db.query(MemoryChunk.content).filter(
                MemoryChunk.id.in_(chunk_ids)
            ).all()

            # .all() returns a list of tuples, so we extract the first item
            return [chunk.content for chunk in relevant_chunks]
            
        except Exception as e:
            print(f"Error in retrieve_relevant_chats: {e}")
            return []

    # --- Override unused abstract methods ---
    def add(self, data: str, metadata: dict = None):
        print("EpisodicMemory: Use add_chat_message(session_id, text) instead.")
        pass

    def retrieve(self, query: str, top_k: int = 5) -> list:
        print("EpisodicMemory: Use retrieve_relevant_chats(query_text) instead.")
        return []

    def clear(self):
        print("Clearing Episodic Memory (not fully implemented)...")
        pass