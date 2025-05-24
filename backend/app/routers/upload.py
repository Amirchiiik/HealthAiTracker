from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import shutil
import os
from uuid import uuid4

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/")
async def upload_file(file: UploadFile = File(...)):
    # Проверка расширения
    allowed_extensions = ["pdf", "png", "jpg", "jpeg", "heic"]
    filename = file.filename
    ext = filename.split(".")[-1].lower()

    if ext not in allowed_extensions:
        raise HTTPException(status_code=400, detail="Unsupported file format")

    # Уникальное имя
    unique_name = f"{uuid4().hex}.{ext}"
    file_path = os.path.join(UPLOAD_DIR, unique_name)

    # Сохраняем файл
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return JSONResponse(content={"filename": unique_name, "message": "Файл успешно загружен"})
