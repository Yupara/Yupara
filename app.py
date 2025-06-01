from PIL import Image
import io
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
        db.execute("""
            CREATE TABLE IF NOT EXISTS files (
                id INTEGER PRIMARY KEY,
                filename TEXT,
                original_name TEXT,
                file_type TEXT,
                uploader TEXT,
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
    active_connections[username] = websocket
    
    try:
        # Отправляем историю сообщений
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
            
            # Обработка личных сообщений
            if data.startswith("@"):
                receiver, *message = data.split(" ", 1)
                receiver = receiver[1:]  # Убираем @
                message = message[0] if message else ""
                
                if receiver in active_connections:
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    with get_db() as db:
                        db.execute(
                            """INSERT INTO messages 
                            (sender, receiver, message, timestamp, is_private) 
                            VALUES (?, ?, ?, ?, 1)""",
                            (username, receiver, message, timestamp)
                        )
                    
                    # Отправка получателю
                    await active_connections[receiver].send_text(
                        f"!private!{username}: {message}"
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
                
                # Рассылка всем
                for user, conn in active_connections.items():
                    await conn.send_text(f"{username}: {data}")
                    
    finally:
        active_users.discard(username)
        active_connections.pop(username, None)

# Загрузка файлов
@app.post("/upload_file")
async def upload_file(
    file: UploadFile = File(...),
    sender: str = Form(...),
    receiver: str = Form(...),
    compress: bool = Form(default=True)
):
    allowed_image_types = ["jpg", "jpeg", "png", "gif"]
    file_ext = file.filename.split(".")[-1].lower()
    file_name = f"{uuid.uuid4()}.{file_ext}"
    file_path = f"static/uploads/{file_name}"
    
    # Сжимаем изображения если нужно
    if file_ext in allowed_image_types and compress:
        try:
            image = Image.open(io.BytesIO(await file.read()))
            
            if file_ext in ["jpg", "jpeg"]:
                image = image.convert("RGB")
                image.save(file_path, "JPEG", quality=85, optimize=True)
            else:
                image.save(file_path, "PNG", optimize=True)
        except Exception as e:
            print(f"Ошибка сжатия изображения: {e}")
            with open(file_path, "wb") as buffer:
                buffer.write(await file.read())
    else:
        # Обычное сохранение для других файлов
        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())
    
    # Определяем тип контента
    content_type = "image" if file_ext in allowed_image_types else "file"
    
    # Сохраняем информацию о файле в БД
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with get_db() as db:
        db.execute(
            """INSERT INTO files 
            (filename, original_name, file_type, uploader, timestamp) 
            VALUES (?, ?, ?, ?, ?)""",
            (file_name, file.filename, content_type, sender, timestamp)
        )
    
    # Отправляем уведомление в чат
    if receiver == "all":
        for conn in active_connections.values():
            await conn.send_text(f"!file!{sender}:{content_type}:/uploads/{file_name}")
    elif receiver in active_connections:
        await active_connections[receiver].send_text(f"!file!{sender}:{content_type}:/uploads/{file_name}")
    
    return {"status": "success", "file_path": f"/uploads/{file_name}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
