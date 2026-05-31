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
        "preview": df.head().to_dict(orient="records"),
        "data_types": df.dtypes.astype(str).to_dict(),
        "missing_values": df.isnull().sum().to_dict(),
        "duplicate_rows": int(df.duplicated().sum()),
        "numeric_summary": df.describe(include=["number"]).to_dict()
    }