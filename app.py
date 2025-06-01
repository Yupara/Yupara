from fastapi import FastAPI, WebSocket, Request, Form
from fastapi.responses import HTMLResponse  # Добавьте этот импорт
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import sqlite3
from datetime import datetime

app = FastAPI()

# Настройка статических файлов
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# База данных
def get_db():
    conn = sqlite3.connect("p2p.db")
    conn.row_factory = sqlite3.Row
    return conn

# Инициализация БД
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

# Главная страница с формой ввода имени
@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

# Обработка формы
@app.post("/chat")
async def start_chat(request: Request, username: str = Form(...)):
    return templates.TemplateResponse(
        "chat.html",
        {"request": request, "username": username}
    )

# WebSocket-чат
@app.websocket("/ws/{username}")
async def chat_endpoint(websocket: WebSocket, username: str):
    await websocket.accept()
    
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
