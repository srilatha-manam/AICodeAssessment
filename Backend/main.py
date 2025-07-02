from fastapi import FastAPI
from routers import (
    ai_code_assessment_routers as evaluation,
    conditional_code_assessment_router as conditional_evaluation
)
from exception_handler import add_exception_handlers

from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI(
    title="AI Code Assessment App",
    version="1.0.0"
)

app.include_router(evaluation.router)
app.include_router(conditional_evaluation.router)

add_exception_handlers(app)

@app.get("/")
async def root():
    return {"status": "Backend live", "message": "AI Code Assessment running"}
@app.get("/healthz")
async def health_check():
    return {"status": "ok"}