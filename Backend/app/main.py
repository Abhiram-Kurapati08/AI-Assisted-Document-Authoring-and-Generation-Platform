from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
import uvicorn

from . import models, schemas, database
from .routers import auth, projects, sections, refine, export
from .config import settings

# Create database tables
models.Base.metadata.create_all(bind=database.engine)

# Initialize FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="AI-Assisted Document Authoring and Generation Platform API",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(projects.router)
app.include_router(sections.router)
app.include_router(refine.router)
app.include_router(export.router)

# Health check endpoint
@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """Health check endpoint for load balancers and monitoring."""
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION
    }

# Root endpoint
@app.get("/", status_code=status.HTTP_200_OK)
async def root():
    """Root endpoint with API information."""
    return {
        "message": f"Welcome to {settings.PROJECT_NAME} API",
        "version": settings.VERSION,
        "docs": "/docs",
        "redoc": "/redoc"
    }

# Database dependency
def get_db():
    """Dependency for getting database session."""
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Run the application
if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        workers=4
    )
