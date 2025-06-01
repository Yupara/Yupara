from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import os
from typing import List, Dict

app = FastAPI()

# Настройка папок для шаблонов и статики
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Временная "база данных" (в памяти)
ads_db: List[Dict] = [
    {"id": 1, "type": "sell", "asset": "USDT", "price": 90, "amount": 1000},
    {"id": 2, "type": "buy", "asset": "BTC", "price": 2500000, "amount": 0.05}
]

# Главная страница
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "ads": ads_db}
    )

# Добавление объявления
@app.post("/create_ad")
async def create_ad(
    type: str = Form(...),
    asset: str = Form(...),
    price: float = Form(...),
    amount: float = Form(...)
):
    new_ad = {
        "id": len(ads_db) + 1,
        "type": type,
        "asset": asset,
        "price": price,
        "amount": amount
    }
    ads_db.append(new_ad)
    return {"status": "success", "ad": new_ad}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
