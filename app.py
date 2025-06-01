from fastapi import FastAPI, WebSocket, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import sqlite3
from datetime import datetime

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# База данных
def get_db():
    return sqlite3.connect("p2p.db")

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

# Главная страница с формой ввода имени
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

# Страница чата
@app.post("/chat", response_class=HTMLResponse)
async def start_chat(request: Request, username: str = Form(...)):
    return templates.TemplateResponse(
        "chat.html",
        {"request": request, "username": username}
    )

# WebSocket-чат
@app.websocket("/ws/{username}")
async def chat(websocket: WebSocket, username: str):
    await websocket.accept()
    db = get_db()
    
    # Отправляем историю
    history = db.execute("SELECT * FROM messages").fetchall()
    for msg in history:
        await websocket.send_text(f"{msg[2]}: {msg[3]} ({msg[4]})")
    
    # Прием новых сообщений
    while True:
        message = await websocket.receive_text()
        time = datetime.now().strftime("%H:%M")
        db.execute(
            "INSERT INTO messages (ad_id, sender, text, time) VALUES (?, ?, ?, ?)",
            (1, username, message, time)  # ad_id=1 для примера
        )
        db.commit()
        await websocket.send_text(f"Вы: {message} ({time})")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
