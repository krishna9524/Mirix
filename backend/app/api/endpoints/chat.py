from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.orm import Session
from app.models.schemas import ChatMessageCreate, TitleGenerateRequest
from app.core.database import get_db
from app.agents.orchestrator import AgentOrchestrator
from fastapi.responses import StreamingResponse
import asyncio
import json

router = APIRouter()

# Dependency for the orchestrator
def get_orchestrator(db: Session = Depends(get_db)):
    # Note: Using the correct, existing class name (AgentOrchestrator)
    return AgentOrchestrator(db_session=db)

# ==============================
# 🤖 CHAT STREAM ENDPOINT
# ==============================================================
@router.post("/chat-stream")
async def post_chat_stream(
    payload: ChatMessageCreate,
    request: Request,
    orchestrator: AgentOrchestrator = Depends(get_orchestrator)
):
    """
    Receives chat history and streams back the response using FastAPI's StreamingResponse.
    """
    
    async def event_generator():
        try:
            # astream_query is the async generator method, the *args accepts the unused arguments
            # passed by Starlette/FastAPI during dependency resolution.
            async for chunk_json in orchestrator.astream_query(payload.messages):
                # Check if the client has disconnected (user closed window/tab)
                if await request.is_disconnected():
                    print("Client disconnected, stopping stream.")
                    break
                
                # Send the chunk of data in Server-Sent Events (SSE) format
                yield f"data: {chunk_json}\n\n"
                await asyncio.sleep(0.001) # Small pause to prevent blocking
                
        except asyncio.CancelledError:
            print("Stream was cancelled.")
        except Exception as e:
            print(f"❌ Chat stream error: {e}")
            # Send a specific error message payload in the stream
            yield f"data: {json.dumps({'type': 'error', 'content': f'Internal Error: {str(e)}'})}\n\n"
        finally:
            print("Stream finished.")
            yield "data: [DONE]\n\n" # Signal the frontend that we are done

    return StreamingResponse(event_generator(), media_type="text/event-stream")
# ==============================================================


# ==============================
# Generate Title Endpoint
# ==================================
@router.post("/generate-title")
def generate_conversation_title(
    payload: TitleGenerateRequest,
    orchestrator: AgentOrchestrator = Depends(get_orchestrator)
):
    """
    Generates a short, descriptive title for a chat session.
    """
    try:
        # orchestrator.generate_title is a synchronous method
        title = orchestrator.generate_title(payload.messages)
        return {"title": title}
    except Exception as e:
        print(f"❌ Title generation error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate title: {str(e)}")