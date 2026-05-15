from sqlalchemy.orm import Session
from typing import List, AsyncGenerator
import json
import os

from app.agents.tools import EpisodicMemoryTool, ImageSearchTool
from app.memory_system.episodic_memory import EpisodicMemory
from app.memory_system.resource_memory import ResourceMemory 
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from app.models.schemas import HistoryMessage 

from langchain_community.tools import DuckDuckGoSearchRun
from langchain_ollama import ChatOllama
from langgraph.prebuilt import create_react_agent

TEXT_EXTENSIONS = {
    ".pdf", ".docx", ".txt", ".md", ".py", ".js", ".css", ".html",
    ".cpp", ".c", ".h", ".java", ".json"
}

class AgentOrchestrator:

    def __init__(self, db_session: Session):
        print("Initializing Multi-Agent Orchestrator with Ollama...")
        self.db = db_session
        
        self.llm = ChatOllama(
            model="qwen2.5-coder:14b",
            base_url="http://localhost:11434", 
            temperature=0.7,
        )
        
        self.tools = [
            EpisodicMemoryTool(db=self.db),
            ImageSearchTool(db=self.db),
            DuckDuckGoSearchRun(name="web_search", description="Search the live internet for current events, facts, or real-time information.")
        ]
        
        self.agent_executor = create_react_agent(self.llm, self.tools)
        self.episodic_memory_saver = EpisodicMemory(self.db)
        self.resource_memory = ResourceMemory(self.db)
        
        print("Multi-Agent Orchestrator initialized.")

    def safe_model_validate(self, msg):
        try:
            if isinstance(msg, HistoryMessage): return msg
            if isinstance(msg, dict): return HistoryMessage.model_validate(msg)
            return None
        except Exception:
            return None

    async def astream_query(self, messages_history: List, *args) -> AsyncGenerator[str, None]:
        if not messages_history:
            yield json.dumps({"type": "token", "content": "How can I help you?"})
            return

        try:
            validated_messages = [self.safe_model_validate(msg) for msg in messages_history]
            validated_messages = [msg for msg in validated_messages if msg is not None]
        except Exception as e:
            yield json.dumps({"type": "error", "content": "Internal validation error."})
            return
        
        if not validated_messages:
            yield json.dumps({"type": "token", "content": "How can I help you?"})
            return
        
        last_user_message = next((msg for msg in reversed(validated_messages) if msg.sender == 'user'), None)
        if not last_user_message:
            yield json.dumps({"type": "token", "content": "Please send a valid message."})
            return
        
        session_id = validated_messages[0].id
        self.episodic_memory_saver.add_chat_message(session_id, last_user_message.text)
        
        try:
            lc_messages = self.convert_history(validated_messages)
        except Exception as e:
            yield json.dumps({"type": "error", "content": f"Error processing file: {e}"})
            return
        
        final_response_text = ""
        try:
            async for msg, metadata in self.agent_executor.astream({"messages": lc_messages}, stream_mode="messages"):
                
                if msg.type == "ai":
                    # A. Stream standard text generation
                    if msg.content and isinstance(msg.content, str):
                        final_response_text += msg.content
                        yield json.dumps({"type": "token", "content": msg.content})
                    
                    # B. Catch tool calls safely
                    tool_calls = getattr(msg, "tool_call_chunks", []) or getattr(msg, "tool_calls", [])
                    for chunk in tool_calls:
                        if "name" in chunk and chunk["name"]:
                            print(f"--- Agent executing tool: {chunk['name']} ---")
                            yield json.dumps({"type": "tool_start", "content": f"Agent using tool: {chunk['name']}..."})
                
                # --- NEW DEBUG FIX: Print what the tool actually found to your terminal ---
                elif msg.type == "tool":
                    print(f"\n[DEBUG] Tool '{msg.name}' returned data: {msg.content[:300]}...\n")

            if final_response_text.strip():
                session_id = validated_messages[0].id
                self.episodic_memory_saver.add_chat_message(session_id, final_response_text)
            else:
                yield json.dumps({"type": "error", "content": "⚠️ The agent completed its thought process but returned no text."})

        except Exception as e:
            print(f"Error in astream_query: {e}")
            yield json.dumps({"type": "error", "content": f"AI Error: {str(e)}"})

    def generate_title(self, messages_history: List[HistoryMessage]) -> str:
        validated_messages = [self.safe_model_validate(msg) for msg in messages_history]
        validated_messages = [msg for msg in validated_messages if msg is not None]
        if not validated_messages:
             return "New Chat"

        lc_messages = self.convert_history(validated_messages)
        lc_messages.append(
            SystemMessage(content="Analyze the conversation above. Respond with only a short, 3-5 word title for this chat. Do not include quotes, punctuation, or any other text.")
        )
        try:
            llm_response = self.llm.invoke(lc_messages)
            title = llm_response.content.strip().strip('\"\'')
            return title
        except Exception as e:
            return "Chat Summary" 

    def convert_history(self, messages_history: List[HistoryMessage]) -> list:
        # --- FIX: Aggressive "Jailbreak" Prompt ---
        system_prompt = """You are MIRIX, an advanced AI assistant. You HAVE full, real-time internet access via the 'web_search' tool.
        
        CRITICAL RULES:
        1. NEVER say "I don't have real-time access" or "I cannot browse the internet". You CAN and MUST use your web_search tool.
        2. When a user asks about current events, weather, or live facts, you MUST use the web_search tool immediately.
        3. Once the tool returns the search results, read them carefully, and give the user the exact answer based ONLY on those results.
        4. Do not apologize. Do not explain your limitations. Just use the tool and answer the question.
        """
        
        lc_messages = [SystemMessage(content=system_prompt)]
        
        last_file_message = next((msg for msg in reversed(messages_history) if msg.fileId is not None), None)
        file_context_added = False

        for msg in messages_history:
            content_parts = [{"type": "text", "text": msg.text}]
            
            if last_file_message and msg.id == last_file_message.id and not file_context_added:
                file_text = self.resource_memory.get_file_content(msg.fileId)
                if not file_text:
                    file_text = "[Error: Could not retrieve file content]"
                
                if len(file_text) > 4000:
                    file_text = file_text[:4000] + "\n\n... [File content truncated] ..."
                
                content_parts[0]["text"] = f"[FILE CONTEXT: {msg.fileName}]\n\n{file_text}\n\n[USER PROMPT]\n{msg.text}"
                file_context_added = True

            if msg.sender == 'user':
                lc_messages.append(HumanMessage(content=content_parts))
            elif msg.sender == 'ai':
                lc_messages.append(AIMessage(content=msg.text))
        
        return lc_messages