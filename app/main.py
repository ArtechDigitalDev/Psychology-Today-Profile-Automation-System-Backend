"""
main.py
Entrypoint for the FastAPI application.
"""
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.api.router import router as api_router
from app.schemas.response import APIResponse

app = FastAPI(
    title="Psychology Today Profile Automation System",
    description="AI-powered automation for managing Psychology Today therapist profiles.",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8080",  # Your frontend URL
        "http://localhost:3000",  # Alternative frontend port
        "http://127.0.0.1:8080",  # Alternative localhost
        "http://127.0.0.1:3000",  # Alternative localhost
        "http://localhost:5173",  # Vite default port
        "http://localhost:4173",  # Vite preview port
        "*"  # Allow all origins (for development only)
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router)

# Root endpoint
default_message = {
    "message": "Welcome to the Psychology Today Profile Automation System API."
}

@app.get("/", tags=["Root"])
def read_root():
    """Root endpoint for health check."""
    return default_message

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "error": str(exc)}
    )

@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    if exc.status_code == 401:
        return JSONResponse(
            status_code=401,
            content=APIResponse(success=False, message="Authentication required. Please provide a valid token.", data=None).model_dump()
        )
    return JSONResponse(
        status_code=exc.status_code,
        content=APIResponse(success=False, message=exc.detail, data=None).model_dump()
    ) 