from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import os

# 1. Создаем приложение
app = FastAPI()

# 2. Настраиваем папки для HTML и CSS
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# 3. База данных для объявлений (пока просто список)
ads_db = [
    {"id": 1, "title": "Продам USDT", "price": 90},
    {"id": 2, "title": "Куплю BTC", "price": 2500000}
]

# 4. Главная страница (P2P-доска)
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "ads": ads_db})

# 5. Добавление объявления
@app.post("/add_ad")
async def add_ad(title: str, price: float):
    new_ad = {"id": len(ads_db)+1, "title": title, "price": price}
    ads_db.append(new_ad)
    return {"status": "success"}
