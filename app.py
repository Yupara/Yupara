from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
import os

app = FastAPI()

# Создаем папку для объявлений, если её нет
os.makedirs("ads", exist_ok=True)

# Ваши текущие роуты (например, главная страница)
@app.get("/")
async def home():
    return {"message": "Добро пожаловать в P2P обменник!"}

# ▼▼▼ Добавьте этот новый эндпоинт ▼▼▼
@app.post("/upload_ad")
async def upload_ad(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        file_path = f"ads/{file.filename}"
        
        with open(file_path, "wb") as f:
            f.write(contents)
            
        return JSONResponse(
            status_code=200,
            content={"message": "Файл загружен", "filename": file.filename}
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"message": f"Ошибка загрузки: {str(e)}"}
        )

# Запуск сервера (если используете __main__)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
