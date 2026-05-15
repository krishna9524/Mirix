from .base_memory import BaseMemory
from sqlalchemy.orm import Session
from app.models.db_models import ResourceMemory as ResourceMemoryModel # Import the new model
from app.models.db_models import MemoryChunk as MemoryChunkModel # Import MemoryChunk to get content

class ResourceMemory(BaseMemory):

    def __init__(self, db_session: Session):
        super().__init__(db_session)
        print("Initializing Resource Memory (now using DB)...")

    def add_file_metadata(self, file_id: str, filename: str, path: str, chunk_id: int):
        """
        Adds file metadata to the persistent SQL Database.
        """
        new_resource = ResourceMemoryModel(
            file_id=file_id,
            original_filename=filename,
            storage_path=path,
            chunk_fk=chunk_id
        )
        self.db.add(new_resource)
        self.db.commit()
        print(f"Added file metadata {file_id} to Database.")

    def get_file_metadata(self, file_id: str) -> dict or None:
        """
        Retrieves persistent file metadata from the SQL Database.
        """
        print(f"Retrieving metadata for file {file_id} from Database.")
        record = self.db.query(ResourceMemoryModel).filter_by(file_id=file_id).first()
        
        if record:
            return {
                'original_filename': record.original_filename,
                'path': record.storage_path,
                'chunk_id': record.chunk_fk # Used for RAG lookup
            }
        return None

    def get_file_content(self, file_id: str) -> str or None:
        """
        Retrieves extracted file content from the linked MemoryChunk.
        """
        metadata = self.get_file_metadata(file_id)
        if metadata and metadata.get('chunk_id'):
            chunk = self.db.query(MemoryChunkModel).filter_by(id=metadata['chunk_id']).first()
            if chunk:
                return chunk.content
        return None
    
    # --- Override unused abstract methods ---
    def add(self, data: str, metadata: dict = None):
        """Not used for persistent file storage."""
        pass

    def retrieve(self, query: str, top_k: int = 5) -> list:
        """Not used for persistent file storage."""
        return []

    def clear(self):
        # Delete all records from the table
        self.db.query(ResourceMemoryModel).delete()
        self.db.commit()
        print("Cleared Resource Memory (SQL).")