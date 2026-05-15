from .base_agent import BaseAgent
from typing import Dict

class FactRetrieverAgent(BaseAgent):

    def __init__(self, memory_system: Dict):
        super().__init__(memory_system)

    def execute(self, task: str, context: dict = None) -> str:
        # TODO: Implement logic to retrieve legal facts
        # This would query the KnowledgeVault and/or SemanticMemory
        print(f"FactRetrieverAgent executing task: {task}")
        
        # Access a specific memory
        knowledge_vault = self.memory_system.get("knowledge_vault")
        if knowledge_vault:
            retrieved_facts = knowledge_vault.retrieve(query=task, top_k=3)
            return f"Retrieved facts: {retrieved_facts}"
        
        return "FactRetrieverAgent: Knowledge Vault not found."