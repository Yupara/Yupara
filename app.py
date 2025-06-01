from fastapi import FastAPI, WebSocket, Request, Form, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import sqlite3
from datetime import datetime
from typing import Dict, Set

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Хранилище активных пользователей
active_users: Set[str] = set()

# База данных
def get_db():
    conn = sqlite3.connect("p2p.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY,
                username TEXT,
                message TEXT,
                timestamp TEXT
            )
        """)

init_db()

# Главная страница
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

# Страница чата
@app.post("/chat", response_class=HTMLResponse)
async def chat_page(request: Request, username: str = Form(...)):
    return templates.TemplateResponse(
        "chat.html",
        {
            "request": request,
            "username": username,
            "active_users": list(active_users)
        }
    )

# WebSocket-чат
@app.websocket("/ws/{username}")
async def chat_endpoint(websocket: WebSocket, username: str):
    await websocket.accept()
    active_users.add(username)
    
    try:
        # Отправляем историю сообщений
        with get_db() as db:
            history = db.execute("SELECT * FROM messages").fetchall()
            for msg in history:
                await websocket.send_text(f"{msg['username']}: {msg['message']}")

        # Принимаем новые сообщения
        while True:
            message = await websocket.receive_text()
            timestamp = datetime.now().strftime("%H:%M:%S")
            
            with get_db() as db:
                db.execute(
                    "INSERT INTO messages (username, message, timestamp) VALUES (?, ?, ?)",
                    (username, message, timestamp)
                )
            
            await websocket.send_text(f"Вы: {message}")
    finally:
        active_users.remove(username)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
