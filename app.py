from fastapi import FastAPI, WebSocket, Request
from fastapi.responses import HTMLResponse
import os

# 1. Создаем объект приложения (это обязательно!)
app = FastAPI()

# 2. Корневой эндпоинт (проверка работы)
@app.get("/")
async def home():
    return {"message": "Сервер работает!"}

# 3. Ваши дополнительные эндпоинты (регистрация, объявления и т.д.)
# ... (вставьте сюда код из предыдущих шагов)

# 4. Запуск сервера (если нужно)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
