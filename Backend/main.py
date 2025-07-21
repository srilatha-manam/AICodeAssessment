from fastapi import FastAPI
import asyncio
import httpx
from routers import (
    ai_code_assessment_routers as evaluation  
)
from exception_handler import add_exception_handlers
from dotenv import load_dotenv


load_dotenv()

app = FastAPI(
    title="AI Code Assessment App",
    version="1.0.0"
)
app.include_router(evaluation.router)
add_exception_handlers(app)

@app.get("/")
async def root():
    return {"status": "Backend live", "message": "AI Code Assessment running"}
@app.get("/healthz")
async def health_check():
    return {"status": "ok"}
async def self_ping_task():
    await asyncio.sleep(60)  # initial delay
    url = "https://aicodeassessment-backend.onrender.com/healthz"
    while True:
        try:
            async with httpx.AsyncClient() as client:
                await client.get(url, timeout=5)
        except Exception:
            pass
        await asyncio.sleep(600)  # ping every 10 minutes
