from fastapi import FastAPI

from backend.app.api import health
from backend.app.api import upload
from backend.app.api import analysis
from backend.app.api import query

app = FastAPI(title="Autonomous Data Analyst")

app.include_router(
health.router,
prefix="/api/v1/health",
tags=["Health"],
)

app.include_router(
upload.router,
prefix="/api/v1/upload",
tags=["Upload"],
)

app.include_router(
analysis.router,
prefix="/api/v1/analysis",
tags=["Analysis"],
)

app.include_router(
query.router,
prefix="/api/v1/query",
tags=["Query"],
)

@app.get("/")
async def root():
 return {"message": "Backend is running successfully"}
