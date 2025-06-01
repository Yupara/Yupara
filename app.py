import os
from fastapi import FastAPI

app = FastAPI()
port = int(os.environ.get("PORT", 8080))  # Берёт порт из переменной Railway или 8080 для локального теста

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=port)
