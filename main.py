from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import router

# Create FastAPI app
app = FastAPI(
    title="Demographic Profile API",
    description="API to manage demographic profiles with external API integration",
    version="1.0.0"
)

#CORS middleware to allow cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

#routes
app.include_router(router)


@app.get("/", tags=["root"])
def read_root():
    """Root endpoint"""
    return {
        "message": "Demographic Profile API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health", tags=["health"])
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
