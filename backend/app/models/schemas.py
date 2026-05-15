from pydantic import BaseModel
from typing import Optional, List

class HistoryMessage(BaseModel):
    id: str
    sender: str
    text: str
    fileId: Optional[str] = None
    fileName: Optional[str] = None
    type: Optional[str] = None

class ChatMessageCreate(BaseModel):
    messages: List[HistoryMessage]

# --- FIX: Re-adding the missing class definition ---
class TitleGenerateRequest(BaseModel):
    messages: List[HistoryMessage]
# --- END FIX ---

class MemoryQuery(BaseModel):
    query: str
    memory_types: Optional[List[str]] = None