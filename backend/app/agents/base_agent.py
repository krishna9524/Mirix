from abc import ABC, abstractmethod
from typing import Dict

class BaseAgent(ABC):

    def __init__(self, memory_system: Dict):
        self.memory_system = memory_system
        print(f"Initializing {self.__class__.__name__}")

    @abstractmethod
    def execute(self, task: str, context: dict = None) -> str:
        """Execute a specific task."""
        pass
