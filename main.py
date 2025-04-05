"""
QA Model Application - FastAPI Backend
Main application entry point
"""
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from api.routes import router as api_router
from utils.logging_utils import setup_logging
from config import settings

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="QA Model Application",
    description="API for question answering using various Hugging Face models",
    version="0.1.0"
)

# Configure CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api")

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"message": "An unexpected error occurred. Please try again later."}
    )

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Root endpoint with API information
@app.get("/")
async def root():
    return {
        "app_name": "QA Model Application",
        "version": "0.1.0",
        "api_docs": "/docs",
        "health_check": "/health"
    }

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting QA Model Application server")
    uvicorn.run("main:app", host="0.0.0.0", port=settings.PORT, reload=True)