from fastapi import FastAPI
from app.bot.webhook import router
from app.services.scheduler import start_scheduler
from app.utils.logger import logger

app = FastAPI()

app.include_router(router)

@app.on_event("startup")
async def startup_event():
    logger.info("Starting scheduler...")
    start_scheduler()
    logger.info("Bot started!")

@app.get("/healthz")
def health():
    return {"status": "ok"}
