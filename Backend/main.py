from fastapi import FastAPI
from .routers import interview


# This module initializes the FastAPI application and includes the interview router.

app = FastAPI(
    title="AI Code Assessment App",
    version="1.0.0"
)
# Include the interview router to handle code assessment related endpoints
app.include_router(interview.router)