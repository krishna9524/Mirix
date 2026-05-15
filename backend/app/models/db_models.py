#from sqlalchemy import Column, String, Integer, Text, ForeignKey
#from sqlalchemy.orm import relationship
#from app.core.database import Base

# This is a central table for all memory "chunks" (text content)
#class MemoryChunk(Base):
 #   __tablename__ = "memory_chunks"
    
  #  id = Column(Integer, primary_key=True, index=True)
   # memory_type = Column(String, index=True, nullable=False) # e.g., "episodic", "resource"
    #content = Column(Text, nullable=False) # Extracted text/metadata

    # Relationships for linking back to specific memory types
    #episodic_memory_id = Column(Integer, ForeignKey("episodic_memory.id"), nullable=True)
    #semantic_memory_id = Column(Integer, ForeignKey("semantic_memory.id"), nullable=True)
    
    #episodic_memory = relationship("EpisodicMemory", back_populates="chunks")
    #semantic_memory = relationship("SemanticMemory", back_populates="chunks")

    # NEW: Relationship for resource memory metadata
    #resource_metadata = relationship("ResourceMemory", back_populates="content_chunk", uselist=False)


#class EpisodicMemory(Base):
    #__tablename__ = "episodic_memory"
   # id = Column(Integer, primary_key=True, index=True)
  #  session_id = Column(String, index=True)
 #   chunks = relationship("MemoryChunk", back_populates="episodic_memory")

#class SemanticMemory(Base):
   # __tablename__ = "semantic_memory"
   # id = Column(Integer, primary_key=True, index=True)
  #  fact = Column(String, unique=True)
 #   chunks = relationship("MemoryChunk", back_populates="semantic_memory")

# --- NEW: PERSISTENT RESOURCE MEMORY MODEL ---
#class ResourceMemory(Base):
    #"""Stores persistent metadata about uploaded files."""
   # __tablename__ = "resource_memory"
    
    # We use the file_id string (UUID) as the primary key
    #file_id = Column(String, primary_key=True, index=True)
    #original_filename = Column(String, nullable=False)
    # The actual path to the file on disk (e.g., mirix_file_storage/uuid.pdf)
    #storage_path = Column(String, nullable=False)
    
    # Foreign key link to the MemoryChunk that holds the file's extracted text content
    #chunk_fk = Column(Integer, ForeignKey("memory_chunks.id"), nullable=False, unique=True)
    
    # Relationship back to the MemoryChunk object
    #content_chunk = relationship("MemoryChunk", back_populates="resource_metadata", uselist=False)
from sqlalchemy import Column, String, Integer, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

# This is a central table for all memory "chunks" (text content)
class MemoryChunk(Base):
    __tablename__ = "memory_chunks"
    
    id = Column(Integer, primary_key=True, index=True)
    memory_type = Column(String(50), index=True, nullable=False)
    content = Column(Text, nullable=False)

    episodic_memory_id = Column(Integer, ForeignKey("episodic_memory.id"), nullable=True)
    semantic_memory_id = Column(Integer, ForeignKey("semantic_memory.id"), nullable=True)
    
    episodic_memory = relationship("EpisodicMemory", back_populates="chunks")
    semantic_memory = relationship("SemanticMemory", back_populates="chunks")

    resource_metadata = relationship("ResourceMemory", back_populates="content_chunk", uselist=False)


class EpisodicMemory(Base):
    __tablename__ = "episodic_memory"
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(255), index=True)
    chunks = relationship("MemoryChunk", back_populates="episodic_memory")

class SemanticMemory(Base):
    __tablename__ = "semantic_memory"
    id = Column(Integer, primary_key=True, index=True)
    
    # --- THIS IS THE FIX ---
    # 1024 * 4 bytes/char = 4096 bytes, which is > 3072 byte limit
    # We reduce the length to 767 (767 * 4 = 3068 bytes, which is < 3072)
    fact = Column(String(767), unique=True)
    # --- END OF FIX ---
    
    chunks = relationship("MemoryChunk", back_populates="semantic_memory")

class ResourceMemory(Base):
    """Stores persistent metadata about uploaded files."""
    __tablename__ = "resource_memory"
    
    file_id = Column(String(255), primary_key=True, index=True)
    original_filename = Column(String(1024), nullable=False)
    storage_path = Column(String(2048), nullable=False)
    
    chunk_fk = Column(Integer, ForeignKey("memory_chunks.id"), nullable=False, unique=True)
    
    content_chunk = relationship("MemoryChunk", back_populates="resource_metadata", uselist=False)