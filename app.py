from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import os

app = FastAPI()

# Настройка папок
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# База данных (пока просто список)
ads_db = [
    {"id": 1, "title": "Продам USDT", "price": 90},
    {"id": 2, "title": "Куплю BTC", "price": 2500000}
]

# Главная страница
@app.get("/")
async def home(request: Request):
    return {"message": "Сервер работает!"}

# Добавление объявления
@app.post("/add_ad")
async def add_ad(title: str, price: float):
    new_ad = {"id": len(ads_db)+1, "title": title, "price": price}
    ads_db.append(new_ad)
    return {"status": "success"}
