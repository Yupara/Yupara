from fastapi import FastAPI, WebSocket, Request
from fastapi.templating import Jinja2Templates
import os

app = FastAPI()
templates = Jinja2Templates(directory="templates")
port = int(os.environ.get("PORT", 8080))

# WebSocket чат
@app.websocket("/ws")
async def chat(websocket: WebSocket):
    await websocket.accept()
    while True:
        message = await websocket.receive_text()
        await websocket.send_text(f"Вы: {message}")

# Главная страница
@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=port)
@app.get("/admin")
async def admin(request: Request, password: str = ""):
    if password != "ваш-секретный-пароль":
        return {"error": "Доступ запрещён"}
    return templates.TemplateResponse("admin.html", {"request": request})
