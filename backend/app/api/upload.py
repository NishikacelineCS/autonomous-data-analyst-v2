from fastapi import APIRouter, UploadFile, File
import pandas as pd
from io import StringIO
from backend.app.services.profiler import generate_profile
from backend.app.services.analyzer import generate_insights

router = APIRouter()


@router.post("/")
async def upload_dataset(file: UploadFile = File(...)):
    """
    Accept a CSV or Excel file upload.
    Swagger: POST /api/v1/upload/
    """

    content = await file.read()

    csv_string = content.decode("utf-8")

    df = pd.read_csv(StringIO(csv_string))

    profile = generate_profile(df)
    insights = generate_insights(profile)

    return {
    "filename": file.filename,
    **profile,
    "insights": insights
}