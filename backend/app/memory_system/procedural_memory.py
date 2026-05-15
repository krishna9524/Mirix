from .base_memory import BaseMemory
from sqlalchemy.orm import Session

class ProceduralMemory(BaseMemory):

    def __init__(self, db_session: Session):
        super().__init__(db_session)
        print("Initializing Procedural Memory...")

    def add(self, data: str, metadata: dict = None):
        # TODO: Implement logic to store step-by-step processes
        print(f"Adding to Procedural Memory: {data}")
        pass

    def retrieve(self, query: str, top_k: int = 5) -> list:
        # TODO: Implement retrieval of "how-to" guides
        print(f"Retrieving from Procedural Memory based on: {query}")
        return [{"data": "step_1_do_this_step_2_do_that", "score": 0.92}]

    def clear(self):
        # TODO: Implement clearing logic
        print("Clearing Procedural Memory")
        pass
