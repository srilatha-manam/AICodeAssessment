from fastapi import Request, FastAPI
from fastapi.responses import JSONResponse
from .logging_config import logger

# Define a function to add exception handlers to a FastAPI app
def add_exception_handlers(app: FastAPI):
    # Define a global exception handler for the app
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        # Log the unhandled exception
        logger.error(f"Unhandled Exception: {exc}", exc_info=True)
        # Return a JSON response with a 500 status code and a message indicating an unexpected error occurred
        return JSONResponse(
            status_code=500,
            content={"detail": "An unexpected error occurred. Please try again later."}
        )
