from fastapi import FastAPI, WebSocket, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import sqlite3
from datetime import datetime

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Подключаем базу данных
def get_db():
    return sqlite3.connect("p2p.db")

# Создаем таблицы (запустится 1 раз при старте)
def init_db():
    db = get_db()
    db.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY,
            ad_id INTEGER,
            sender TEXT,
            text TEXT,
            time TEXT
        )
    """)
    db.commit()

init_db()

# WebSocket-чат
@app.websocket("/ws/{ad_id}")
async def chat(websocket: WebSocket, ad_id: int):
    await websocket.accept()
    db = get_db()
    
    # Отправляем историю сообщений
    history = db.execute(
        "SELECT sender, text, time FROM messages WHERE ad_id = ?",
        (ad_id,)
    ).fetchall()
    
    for msg in history:
        await websocket.send_text(f"{msg[0]}: {msg[1]} ({msg[2]})")
    
    # Принимаем новые сообщения
    while True:
        message = await websocket.receive_text()
        time = datetime.now().strftime("%H:%M")
        db.execute(
            "INSERT INTO messages (ad_id, sender, text, time) VALUES (?, ?, ?, ?)",
            (ad_id, "Пользователь", message, time)  # Пока без регистрации
        )
        db.commit()
        await websocket.send_text(f"Вы: {message} ({time})")

@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
