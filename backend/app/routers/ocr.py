from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse
import os
from app.services.ocr_service import extract_text_from_file

router = APIRouter()

@router.get("/")
async def perform_ocr(filename: str = Query(..., description="Имя файла из папки uploads")):
    file_path = os.path.join("uploads", filename)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Файл не найден")

    try:
        result = extract_text_from_file(file_path)

        # результат уже словарь с ключами: extracted_text + analysis/pages_analysis
        response = {
            "filename": filename,
            **result
        }

        return JSONResponse(content=response)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
