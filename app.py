from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import os

app = FastAPI()

# Проверка корневого эндпоинта
@app.get("/")
def home():
    return {"message": "Сервер работает!"}

# Эндпоинт для загрузки файлов
@app.post("/upload_ad")
async def upload_ad(file: UploadFile = File(..., max_size=1_000_000)):
    try:
        # Проверка типа файла
        if not file.filename.endswith('.json'):
            raise HTTPException(status_code=400, detail="Только JSON-файлы!")
        
        # Сохранение файла
        file_path = f"ads/{file.filename}"
        os.makedirs("ads", exist_ok=True)
        
        with open(file_path, "wb") as f:
            contents = await file.read()
            f.write(contents)
        
        return JSONResponse(
            content={"status": "success", "file": file.filename},
            status_code=200
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Добавьте это в конец файла, если запускаете напрямую
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
