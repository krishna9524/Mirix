from fastapi import APIRouter

router = APIRouter()

@router.get("/agents")
def get_available_agents():
    """
    Get a list of all available specialized agents.
    """
    # This can be hardcoded or dynamically generated
    return {"agents": ["fact_retriever", "statute_interpreter"]}
