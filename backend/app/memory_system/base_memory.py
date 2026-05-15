from abc import ABC, abstractmethod
from sqlalchemy.orm import Session

class BaseMemory(ABC):
    
    def __init__(self, db_session: Session):
        self.db = db_session

    @abstractmethod
    def add(self, data: str, metadata: dict = None):
        """Add data to this memory type."""
        pass

    @abstractmethod
    def retrieve(self, query: str, top_k: int = 5) -> list:
        """Retrieve relevant data from this memory type."""
        pass

    @abstractmethod
    def clear(self):
        """Clear this memory type."""
        pass