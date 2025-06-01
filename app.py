from fastapi import FastAPI, WebSocket, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import sqlite3
from datetime import datetime
from typing import Dict, Set
import os
import uuid

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Проверяем и создаем необходимые папки
os.makedirs("static/uploads", exist_ok=True)

# Хранилище активных подключений
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

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return {"message": "P2P Chat is working!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
from fastapi import WebSocket
from typing import Dict, Set

# Добавляем после импортов
active_connections: Dict[str, WebSocket] = {}
active_users: Set[str] = set()

# Добавляем перед if __name__ == "__main__":
@app.websocket("/ws/{username}")
async def websocket_chat(websocket: WebSocket, username: str):
    await websocket.accept()
    active_connections[username] = websocket
    active_users.add(username)
    
    try:
        while True:
            message = await websocket.receive_text()
            # Рассылаем всем участникам
            for connection in active_connections.values():
                await connection.send_text(f"{username}: {message}")
    finally:
        active_connections.pop(username, None)
        active_users.discard(username)
from datetime import datetime

# Функция для сохранения сообщения в БД
async def save_message(sender: str, message: str, is_private: bool = False, receiver: str = None):
    with get_db() as db:
        db.execute(
            """INSERT INTO messages 
            (sender, receiver, message, timestamp, is_private) 
            VALUES (?, ?, ?, ?, ?)""",
            (sender, receiver, message, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), int(is_private))
        )
        db.commit()

# Обновите WebSocket-эндпоинт:
@app.websocket("/ws/{username}")
async def websocket_chat(websocket: WebSocket, username: str):
    await websocket.accept()
    active_connections[username] = websocket
    active_users.add(username)

    try:
        # Отправляем историю сообщений при подключении
        with get_db() as db:
            history = db.execute("SELECT sender, message FROM messages WHERE is_private = 0 OR receiver = ?", (username,)).fetchall()
            for msg in history:
                await websocket.send_text(f"{msg['sender']}: {msg['message']}")

        while True:
            message = await websocket.receive_text()
            await save_message(username, message)  # Сохраняем в БД
            for conn in active_connections.values():
                await conn.send_text(f"{username}: {message}")
    finally:
        active_connections.pop(username, None)
        active_users.discard(username)
@app.websocket("/ws/{username}")
async def websocket_chat(websocket: WebSocket, username: str):
    await websocket.accept()
    active_connections[username] = websocket
    active_users.add(username)

    try:
        # Отправляем историю общих и личных сообщений
        with get_db() as db:
            history = db.execute(
                "SELECT * FROM messages WHERE is_private = 0 OR receiver = ? OR sender = ?",
                (username, username)
            ).fetchall()
            for msg in history:
                prefix = "[Лично] " if msg['is_private'] else ""
                await websocket.send_text(f"{prefix}{msg['sender']}: {msg['message']}")

        while True:
            message = await websocket.receive_text()
            
            # Если сообщение начинается с @ (личное)
            if message.startswith("@"):
                parts = message.split(" ", 1)
                if len(parts) < 2:
                    continue
                receiver_username = parts[0][1:]  # Убираем @
                private_message = parts[1]
                
                if receiver_username in active_connections:
                    # Сохраняем в БД как личное
                    await save_message(
                        sender=username,
                        message=private_message,
                        is_private=True,
                        receiver=receiver_username
                    )
                    # Отправляем получателю
                    await active_connections[receiver_username].send_text(
                        f"[Лично] {username}: {private_message}"
                    )
                    # Отправляем отправителю для подтверждения
                    await websocket.send_text(
                        f"[Вы → {receiver_username}]: {private_message}"
                    )
            else:
                # Общее сообщение
                await save_message(username, message)
                for conn in active_connections.values():
                    await conn.send_text(f"{username}: {message}")
                    
    finally:
        active_connections.pop(username, None)
        active_users.discard(username)
