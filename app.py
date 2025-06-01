from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
import sqlite3

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# База данных
def get_db():
    return sqlite3.connect("p2p.db")

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

init_db()

# Главная страница
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    db = get_db()
    ads = db.execute("SELECT * FROM ads").fetchall()
    return templates.TemplateResponse(
        "index.html", 
        {"request": request, "ads": ads}
    )

# Создание объявления
@app.post("/create_ad")
async def create_ad(
    type: str = Form(...),
    asset: str = Form(...),
    price: float = Form(...),
    amount: float = Form(...)
):
    db = get_db()
    db.execute(
        "INSERT INTO ads (type, asset, price, amount) VALUES (?, ?, ?, ?)",
        (type, asset, price, amount)
    )
    db.commit()
    return RedirectResponse(url="/", status_code=303)

# Обработка покупки
@app.post("/buy/{ad_id}")
async def buy_ad(ad_id: int):
    db = get_db()
    ad = db.execute("SELECT * FROM ads WHERE id = ?", (ad_id,)).fetchone()
    
    if not ad:
        return {"status": "error", "message": "Объявление не найдено"}
    
    # Здесь будет логика сделки (пока просто удаляем объявление)
    db.execute("DELETE FROM ads WHERE id = ?", (ad_id,))
    db.commit()
    return RedirectResponse(url="/", status_code=303)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
