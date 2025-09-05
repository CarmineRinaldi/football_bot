import os
import asyncio
from fastapi import FastAPI
import uvicorn

from app.bot import start_bot
from app.webhook import router as stripe_router

app = FastAPI()
app.include_router(stripe_router)

@app.on_event("startup")
async def startup_event():
    # avvia il bot Telegram in background (start_bot deve essere una coroutine che fa polling o webhook)
    asyncio.create_task(start_bot())

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
