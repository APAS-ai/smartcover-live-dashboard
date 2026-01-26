from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes import router

app = FastAPI(
    title="SmartCover Proxy API",
    description="""
## SmartCover Data Proxy Service

This API provides authenticated access to SmartCover IoT sensor data.

### Authentication
1. Call `POST /api/v1/auth/token` with your credentials
2. Use the returned JWT token in the `Authorization` header: `Bearer <token>`

### Available Endpoints
- **Locations**: Get monitoring site information
- **Live Data**: Real-time sensor readings
- **Historical Data**: Time-series data queries
- **Alarms**: Alarm events and status
- **Alerts**: Alert events and status
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware - configure as needed for your frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix="/api/v1")


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information."""
    return {
        "service": "SmartCover Proxy API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/v1/health",
    }
