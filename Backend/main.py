from fastapi import FastAPI
from routers import (
    ai_code_assessment_routers as evaluation,
    conditional_code_assessment_router as conditional_evaluation)
from exception_handler import add_exception_handlers
from dotenv import load_dotenv
import os
load_dotenv()
# This module initializes the FastAPI application and includes the interview router.

app = FastAPI(
    title="AI Code Assessment App",
    version="1.0.0"
)
# Include the interview router to handle code assessment related endpoints
app.include_router(evaluation.router)
app.include_router(conditional_evaluation.router)
# Exception handlers for the app
add_exception_handlers(app)