from fastapi import FastAPI, WebSocket, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import sqlite3
from datetime import datetime
from typing import Dict, Set

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Хранилище данных
active_connections: Dict[str, WebSocket] = {}
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
                sender TEXT,
                receiver TEXT,
                message TEXT,
                timestamp TEXT,
                is_private INTEGER
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
    active_connections[username] = websocket
    
    try:
        # Отправляем историю общих сообщений
        with get_db() as db:
            history = db.execute(
                "SELECT * FROM messages WHERE is_private = 0 OR receiver = ? OR sender = ?",
                (username, username)
            ).fetchall()
            
            for msg in history:
                prefix = "[Лично]" if msg['is_private'] else ""
                await websocket.send_text(
                    f"{prefix} {msg['sender']}: {msg['message']}"
                )

        # Прием сообщений
        while True:
            data = await websocket.receive_text()
            
            # Формат: "@username сообщение" для личных сообщений
            if data.startswith("@"):
                receiver, *message = data.split(" ", 1)
                receiver = receiver[1:]  # Убираем @
                message = message[0] if message else ""
                
                if receiver in active_connections:
                    # Сохраняем личное сообщение
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    with get_db() as db:
                        db.execute(
                            """INSERT INTO messages 
                            (sender, receiver, message, timestamp, is_private) 
                            VALUES (?, ?, ?, ?, 1)""",
                            (username, receiver, message, timestamp)
                        )
                    
                    # Отправляем получателю
                    await active_connections[receiver].send_text(
                        f"[Лично] {username}: {message}"
                    )
                    await websocket.send_text(
                        f"[Вы → {receiver}]: {message}"
                    )
            else:
                # Общее сообщение
                timestamp = datetime.now().strftime("%H:%M:%S")
                with get_db() as db:
                    db.execute(
                        """INSERT INTO messages 
                        (sender, receiver, message, timestamp, is_private) 
                        VALUES (?, ?, ?, ?, 0)""",
                        (username, "", data, timestamp)
                    )
                
                # Рассылаем всем
                for user, conn in active_connections.items():
                    await conn.send_text(f"{username}: {data}")
                    
    finally:
        active_users.discard(username)
        active_connections.pop(username, None)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
# В методе chat_endpoint замените блок отправки личных сообщений на:
if receiver in active_connections:
    timestamp = datetime.now().strftime("%H:%M:%S")
    with get_db() as db:
        db.execute(
            """INSERT INTO messages 
            (sender, receiver, message, timestamp, is_private) 
            VALUES (?, ?, ?, ?, 1)""",
            (username, receiver, message, timestamp)
        )
    
    # Отправляем получателю с флагом уведомления
    await active_connections[receiver].send_text(
        f"!private!{username}: {message}"
    )
    await websocket.send_text(
        f"[Вы → {receiver}]: {message}"
    )
