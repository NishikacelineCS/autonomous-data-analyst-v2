from fastapi import APIRouter, UploadFile, File
import pandas as pd
from io import StringIO

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

    return {
        "filename": file.filename,
        "rows": len(df),
        "columns": len(df.columns),
        "column_names": df.columns.tolist(),
        "preview": df.head().to_dict(orient="records")
    }