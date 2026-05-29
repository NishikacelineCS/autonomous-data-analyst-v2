from fastapi import APIRouter

router = APIRouter()


@router.post("/run")
async def run_analysis(session_id: str):
    """
    Trigger the multi-agent analysis workflow for an uploaded dataset.
    Swagger: POST /api/v1/analysis/run?session_id=...

    Not yet implemented — returns the session_id for confirmation.
    """
    return {
        "session_id": session_id,
        "status": "pending",
        "message": "Analysis endpoint reached. LangGraph workflow not yet wired.",
    }


@router.get("/status/{session_id}")
async def get_analysis_status(session_id: str):
    """
    Poll the current stage and agent statuses for a running analysis.
    Swagger: GET /api/v1/analysis/status/{session_id}

    Not yet implemented.
    """
    return {
        "session_id": session_id,
        "current_stage": "not_started",
        "message": "Status endpoint reached. Not yet implemented.",
    }


@router.get("/results/{session_id}")
async def get_analysis_results(session_id: str):
    """
    Retrieve the completed analysis results for a session.
    Swagger: GET /api/v1/analysis/results/{session_id}

    Not yet implemented.
    """
    return {
        "session_id": session_id,
        "message": "Results endpoint reached. Not yet implemented.",
    }