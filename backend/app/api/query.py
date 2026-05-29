from fastapi import APIRouter

router = APIRouter()


@router.post("/ask")
async def ask_question(session_id: str, question: str):
    """
    Ask a natural language question about an analysed dataset.
    Swagger: POST /api/v1/query/ask?session_id=...&question=...

    Not yet implemented.
    """
    return {
        "session_id": session_id,
        "question": question,
        "message": "Query endpoint reached. NL processing not yet implemented.",
    }