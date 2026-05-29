from fastapi import APIRouter, UploadFile, File

router = APIRouter()


@router.post("/")
async def upload_dataset(file: UploadFile = File(...)):
    """
    Accept a CSV or Excel file upload.
    Swagger: POST /api/v1/upload/

    Not yet implemented — returns the filename and size for confirmation.
    """
    content = await file.read()
    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "size_bytes": len(content),
        "status": "received",
        "message": "Upload endpoint reached. Processing not yet implemented.",
    }