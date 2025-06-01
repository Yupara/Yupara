from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import os

app = FastAPI()

# Создаем папку для хранения объявлений
os.makedirs("ads", exist_ok=True)

# Ваши существующие роуты
@app.get("/")
async def home():
    return {"message": "P2P Обменник"}

# ▼▼▼ Добавьте этот новый эндпоинт ▼▼▼
@app.post("/upload_ad")
async def upload_ad(file: UploadFile = File(..., max_size=1_000_000)):  # Лимит 1MB
    try:
        # Проверяем расширение файла
        if not file.filename.endswith('.json'):
            raise HTTPException(status_code=400, detail="Только JSON-файлы разрешены")
        
        # Читаем и сохраняем файл
        contents = await file.read()
        file_path = f"ads/{file.filename}"
        
        with open(file_path, "wb") as f:
            f.write(contents)
            
        return JSONResponse(
            status_code=200,
            content={
                "message": "Файл успешно загружен",
                "filename": file.filename,
                "saved_path": file_path
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка загрузки файла: {str(e)}"
        )
