# ----👇 Вставьте этот код в app.py 👇----

# 1. Регистрация пользователей
from pydantic import BaseModel

class User(BaseModel):
    username: str
    password: str

users_db = []  # Временная база (потом заменим на PostgreSQL)

@app.post("/register")
async def register(user: User):
    users_db.append(user)
    return {"status": "success", "user": user.username}

# 2. Создание объявлений
ads_db = []

@app.get("/ads")
async def get_ads():
    return {"ads": ads_db}

@app.post("/create_ad")
async def create_ad(ad: dict):
    ads_db.append(ad)
    return {"status": "ad_created"}

# 3. Чат (тестовый)
from fastapi import WebSocket

@app.websocket("/ws")
async def chat(websocket: WebSocket):
    await websocket.accept()
    while True:
        message = await websocket.receive_text()
        await websocket.send_text(f"Вы: {message}")

# ----👆 Конец вставки 👆----
