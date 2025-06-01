from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import sqlite3
import os

app = FastAPI()

# Настройка папок
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Подключение к SQLite
def get_db():
    conn = sqlite3.connect("p2p.db")
    return conn

# Создаем таблицу объявлений (выполнится один раз при первом запуске)
def init_db():
    db = get_db()
    db.execute("""
        CREATE TABLE IF NOT EXISTS ads (
            id INTEGER PRIMARY KEY,
            type TEXT,
            asset TEXT,
            price REAL,
            amount REAL
        )
    """)
    db.commit()

init_db()  # Инициализируем базу

# Главная страница
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    db = get_db()
    ads = db.execute("SELECT * FROM ads").fetchall()
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "ads": ads}
    )

# Добавление объявления
@app.post("/create_ad")
async def create_ad(
    type: str = Form(...),
    asset: str = Form(...),
    price: float = Form(...),
    amount: float = Form(...)
):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO ads (type, asset, price, amount) VALUES (?, ?, ?, ?)",
        (type, asset, price, amount)
    )
    db.commit()
    return {"status": "success"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
