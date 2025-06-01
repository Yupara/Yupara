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
